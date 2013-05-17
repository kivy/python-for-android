
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <dlfcn.h>
#include <dirent.h>
#include "android/log.h"

//#define LOG(...) __android_log_print(ANDROID_LOG_INFO, "redirect", __VA_ARGS__)
#define LOG(...) 

typedef struct filemap_entry_s {
	const char *source;
	const char dest[PATH_MAX];
	int is_dir;
	struct filemap_entry_s *next;
} filemap_entry_t;

static filemap_entry_t *entries = NULL;
static int basedirlen = 0;
static char basedir[PATH_MAX];
static char libdir[PATH_MAX];

static void filemap_entry_add(char *source, char *dest) {
	filemap_entry_t *entry = (filemap_entry_t *)malloc(sizeof(filemap_entry_t));
	entry->source = source;
	snprintf((char *)entry->dest, PATH_MAX, "%s/%s", libdir, dest);
	entry->next = entries;
	entry->is_dir = 0;
	entries = entry;
}

static void filemap_entry_add_dir(char *source) {
	filemap_entry_t *entry = (filemap_entry_t *)malloc(sizeof(filemap_entry_t));
	entry->source = source;
	snprintf((char *)entry->dest, PATH_MAX, "%s", libdir);
	entry->next = entries;
	entry->is_dir = 1;
	entries = entry;
}

static const char *filemap_entry_find(const char *source) {
	filemap_entry_t *entry = entries;
	while ( entry != NULL ) {
		if ( strcmp(entry->source, source) == 0 )
			return entry->dest;
		entry = entry->next;
	}
	return NULL;
}

static filemap_entry_t *filemap_entry_find_dir(const char *source) {
	filemap_entry_t *entry = entries;
	while ( entry != NULL ) {
		if ( strcmp(entry->source, source) == 0 && entry->is_dir )
			return entry;
		entry = entry->next;
	}
	return NULL;
}

static filemap_entry_t *find_dir(const char *source) {
	if (strncmp(source, basedir, basedirlen) == 0) {
		return filemap_entry_find_dir(source + basedirlen + 1);
	}
	return filemap_entry_find_dir(source);
}

static int file_exists(const char* fn) {
   return access(fn, F_OK) != -1;
}

static const char *mangle(const char *fn) {
	if ( file_exists(fn) ) {
		LOG("  --> really exist on the disk, return the real filename.");
		return fn;
	}

	if (strncmp(fn, basedir, basedirlen) == 0) {
		LOG("  --> search in the filemap(basedir): %s", fn + basedirlen + 1);
		const char *fm = filemap_entry_find(fn + basedirlen + 1);
		LOG("  --> filemap returned %s", fm);
		return fm != NULL ? fm : fn;
	}

	if ( fn[0] == '.' && fn[1] == '/' ) {
		LOG("  --> search in the filemap(.): %s", fn + 2);
		const char *fm3 = filemap_entry_find(fn + 2);
		LOG("  --> filemap returned %s", fm3);
		return fm3 != NULL ? fm3 : fn;
	}

	LOG("  --> search in the filemap(no basedir): %s", fn);
	const char *fm2 = filemap_entry_find(fn);
	LOG("  --> filemap returned %s", fm2);
	return fm2 != NULL ? fm2 : fn;
}

static ssize_t getline(char **lineptr, size_t *n, FILE *stream)
{
    char *ptr;
    ptr = fgetln(stream, n);
    if (ptr == NULL)
        return -1;
    if (*lineptr != NULL)
		free(*lineptr);
    size_t len = n[0] + 1;
    n[0] = len;
    *lineptr = malloc(len);
    memcpy(*lineptr, ptr, len-1);
    (*lineptr)[len-1] = '\0';
    return len;
}

static void __android_init(const char *files_directory, const char *libs_directory) {
	char *line = NULL;
	size_t len = 0;
	char *sep;
	char destfn[PATH_MAX];
	int count = 0;

	LOG("-- android low-level redirection started --");

	snprintf(destfn, PATH_MAX, "%s/libfilemap.so", libs_directory);
	memcpy(basedir, files_directory, strlen(files_directory) + 1);
	memcpy(libdir, libs_directory, strlen(libs_directory) + 1);
	basedirlen = strlen(basedir);

	// load the libfilemap.so
	FILE *f = fopen(destfn, "r");
	if (f == NULL) {
		LOG("-- unable to read %s --", destfn);
		return;
	}

	LOG("-- reading %s --", destfn);
	char *c = NULL;
	while (getline(&line, &len, f) != -1) {
		line[strlen(line) - 1] = '\0';
		c = line;
		line += 1;
		if ( *c == 'd' ) {
			// directory
			LOG("-- add directory %s --", line);
			filemap_entry_add_dir(line);
		} else {
			// file
			sep = strchr(line, ';');
			// malformed line ?
			if ( sep == NULL )
				continue;
			*sep = '\0';
			filemap_entry_add(line, sep + 1);
		}
		line = NULL;
		len = 0;
		count += 1;
	}

	fclose(f);
	LOG("-- %d entries read --", count);
}

int __android_open(const char *pathname, int flags, mode_t mode) {
	LOG("-- __android_open(%s) --", pathname);
	return open(mangle(pathname), flags, mode);
}

FILE *__android_fopen(const char *pathname, const char *mode) {
	LOG("-- __android_fopen(%s) --", pathname);
	return fopen(mangle(pathname), mode);
}

FILE *__android_freopen(const char *path, const char *mode, FILE *stream) {
	LOG("-- __android_freopen(%s) --", path);
	return freopen(mangle(path), mode, stream);
}

int __android_stat(const char *path, struct stat *buf) {
	LOG("-- __android_stat(%s) --", path);
	return stat(mangle(path), buf);
}

int __android_lstat(const char *path, struct stat *buf) {
	LOG("-- __android_lstat(%s) --", path);
	return lstat(mangle(path), buf);
}

void * __android_dlopen(const char *filename, int flag) {
	LOG("-- __android_dlopen(%s) --", filename);
	return dlopen(mangle(filename), flag);
}

int __android_access(const char *pathname, int mode) {
	LOG("-- __android_access(%s) --", pathname);
	return access(mangle(pathname), mode);
}


// mem slot 0 - native DIR
// mem slot 1 - directory name
// mem slot 2 - current search
DIR *__android_opendir(const char *name) {
	LOG("-- __android_opendir(%s) --", name);
	void **mem = NULL;
	DIR* ret = NULL;
	filemap_entry_t *entry = find_dir(name);
	if ( entry == NULL ) {
		LOG("  --> native access");
		ret = opendir(name);
		if (ret == NULL)
			return NULL;
		mem = calloc(sizeof(void *) * 3, 1);
		mem[0] = ret;
		return (DIR *)mem;
	} else {
		LOG("  --> wrapped access");
		mem = calloc(sizeof(void *) * 3, 1);
		mem[1] = (void *)entry;
		mem[2] = (void *)entries;
		return (DIR *)mem;
	}
}

struct dirent *__android_readdir(DIR *dirp) {
	LOG("-- __android_readdir(%p) --", dirp);
	void **mem = (void **)dirp;
	char *source;
	static struct dirent d;
	filemap_entry_t *entry;
	filemap_entry_t *basedir;

	// native access
	if (mem[0] != NULL) {
		LOG("  --> native access");
		return readdir((DIR *)mem[0]);
	}

	LOG("  --> wrapped access");

	// search the next file in the directory
	basedir = (filemap_entry_t *)mem[1];
	entry = (filemap_entry_t *)mem[2];
	while ( entry != NULL ) {
		if ( strcmp(basedir->source, entry->source) != 0 )
			goto nextentry;

		source = (char *)entry->source + 1;
		LOG("  --> might found an entry <%s>", entry->source);

		if ( strchr(source, '/') != NULL )
			goto nextentry;

		LOG("  --> selected <%s>", entry->source);

		d.d_ino = 0;
		d.d_off = 0;
		d.d_reclen = sizeof(struct dirent);
		d.d_type = entry->is_dir ? DT_DIR : DT_REG;
		strncpy(d.d_name, entry->source, 256);

		mem[2] = entry->next;
		return &d;

nextentry:;
		entry = entry->next;
	}

	LOG("  --> wrapped access ( end )");
	return NULL;
}

int __android_closedir(DIR *dirp) {
	LOG("-- __android_closedir(%p) --", dirp);
	void **mem = (void **)dirp;
	int ret;

	// native access
	if (mem[0] != NULL) {
		LOG("  --> native access");
		ret = closedir((DIR *)mem[0]);
		free(mem);
		return ret;
	}

	free(mem);
	return 0;
}



// JNI Injection
#include <jni.h>

/* JNI-C++ wrapper stuff */
#ifndef _JNI_WRAPPER_STUFF_H_
#define _JNI_WRAPPER_STUFF_H_

#define SDL_JAVA_PACKAGE_PATH org_renpy_android
#define JAVA_EXPORT_NAME2(name,package) Java_##package##_##name
#define JAVA_EXPORT_NAME1(name,package) JAVA_EXPORT_NAME2(name,package)
#define JAVA_EXPORT_NAME(name) JAVA_EXPORT_NAME1(name,SDL_JAVA_PACKAGE_PATH)

#endif
JNIEXPORT void JNICALL
JAVA_EXPORT_NAME(PythonActivity_nativeRedirect) (JNIEnv* env, jobject thiz,
		jstring j_files_directory, jstring j_libs_directory) {
	jboolean iscopy;
	const char *libs_directory = (*env)->GetStringUTFChars(env, j_libs_directory, &iscopy);
	const char *files_directory = (*env)->GetStringUTFChars(env, j_files_directory, &iscopy);
	__android_init(files_directory, libs_directory);
}
