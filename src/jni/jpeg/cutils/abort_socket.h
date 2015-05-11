/*
 * Copyright 2009, The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/* Helper to perform abortable blocking operations on a socket:
 *   asocket_connect()
 *   asocket_accept()
 *   asocket_read()
 *   asocket_write()
 * These calls are similar to the regular syscalls, but can be aborted with:
 *   asocket_abort()
 *
 * Calling close() on a regular POSIX socket does not abort blocked syscalls on
 * that socket in other threads.
 *
 * After calling asocket_abort() the socket cannot be reused.
 *
 * Call asocket_destory() *after* all threads have finished with the socket to
 * finish closing the socket and free the asocket structure.
 *
 * The helper is implemented by setting the socket non-blocking to initiate
 * syscalls connect(), accept(), read(), write(), then using a blocking poll()
 * on both the primary socket and a local pipe. This makes the poll() abortable
 * by writing a byte to the local pipe in asocket_abort().
 *
 * asocket_create() sets the fd to non-blocking mode. It must not be changed to
 * blocking mode.
 *
 * Using asocket will triple the number of file descriptors required per
 * socket, due to the local pipe. It may be possible to use a global pipe per
 * process rather than per socket, but we have not been able to come up with a
 * race-free implementation yet.
 *
 * All functions except asocket_init() and asocket_destroy() are thread safe.
 */

#include <stdlib.h>
#include <sys/socket.h>

#ifndef __CUTILS_ABORT_SOCKET_H__
#define __CUTILS_ABORT_SOCKET_H__
#ifdef __cplusplus
extern "C" {
#endif

struct asocket {
    int fd;           /* primary socket fd */
    int abort_fd[2];  /* pipe used to abort */
};

/* Create an asocket from fd.
 * Sets the socket to non-blocking mode.
 * Returns NULL on error with errno set.
 */
struct asocket *asocket_init(int fd);

/* Blocking socket I/O with timeout.
 * Calling asocket_abort() from another thread will cause each of these
 * functions to immediately return with value -1 and errno ECANCELED.
 * timeout is in ms, use -1 to indicate no timeout. On timeout -1 is returned
 * with errno ETIMEDOUT.
 * EINTR is handled in-call.
 * Other semantics are identical to the regular syscalls.
 */
int asocket_connect(struct asocket *s, const struct sockaddr *addr,
        socklen_t addrlen, int timeout);

int asocket_accept(struct asocket *s, struct sockaddr *addr,
        socklen_t *addrlen, int timeout);

int asocket_read(struct asocket *s, void *buf, size_t count, int timeout);

int asocket_write(struct asocket *s, const void *buf, size_t count,
        int timeout);

/* Abort above calls and shutdown socket.
 * Further I/O operations on this socket will immediately fail after this call.
 * asocket_destroy() should be used to release resources once all threads
 * have returned from blocking calls on the socket.
 */
void asocket_abort(struct asocket *s);

/* Close socket and free asocket structure.
 * Must not be called until all calls on this structure have completed.
 */
void asocket_destroy(struct asocket *s);

#ifdef __cplusplus
}
#endif
#endif //__CUTILS_ABORT_SOCKET__H__
