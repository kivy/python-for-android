/*
 * Copyright (C) 2007 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

//
// implementation of sys/uio.h for platforms that don't have it (Win32)
//
#ifndef _LIBS_CUTILS_UIO_H
#define _LIBS_CUTILS_UIO_H

#define HAVE_SYS_UIO_H
#ifdef HAVE_SYS_UIO_H
#include <sys/uio.h>
#else

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>

struct iovec {
    const void*  iov_base;
    size_t       iov_len;
};

extern int  readv( int  fd, struct iovec*  vecs, int  count );
extern int  writev( int  fd, const struct iovec*  vecs, int  count );

#ifdef __cplusplus
}
#endif

#endif /* !HAVE_SYS_UIO_H */

#endif /* _LIBS_UTILS_UIO_H */

