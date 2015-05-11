/*
 * Copyright (C) 2006 The Android Open Source Project
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

#ifndef _ADB_NETWORKING_H
#define _ADB_NETWORKING_H 1
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#ifdef __cplusplus
extern "C" {
#endif

extern int adb_networking_connect_fd(int fd, struct sockaddr_in *p_address);
extern int adb_networking_gethostbyname(const char *name, struct in_addr *p_out_addr);

#ifdef __cplusplus
}
#endif

#endif /*_ADB_NETWORKING_H*/

