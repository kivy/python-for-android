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

#ifndef __CUTILS_CPU_INFO_H
#define __CUTILS_CPU_INFO_H

#ifdef __cplusplus
extern "C" {
#endif

/* returns a string contiaining an ASCII representation of the CPU serial number, 
** or NULL if cpu info not available.
** The string is a static variable, so don't call free() on it.
*/
extern const char* get_cpu_serial_number(void);
    
#ifdef __cplusplus
}
#endif

#endif /* __CUTILS_CPU_INFO_H */ 
