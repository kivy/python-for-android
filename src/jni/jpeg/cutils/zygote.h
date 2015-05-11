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

#ifndef __CUTILS_ZYGOTE_H
#define __CUTILS_ZYGOTE_H

#ifdef __cplusplus
extern "C" {
#endif

int zygote_run_oneshot(int sendStdio, int argc, const char **argv);
int zygote_run(int argc, const char **argv);
int zygote_run_wait(int argc, const char **argv, void (*post_run_func)(int));

#ifdef __cplusplus
}
#endif

#endif /* __CUTILS_ZYGOTE_H */
