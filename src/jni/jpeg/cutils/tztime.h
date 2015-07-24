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

#ifndef _CUTILS_TZTIME_H
#define _CUTILS_TZTIME_H

#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

time_t mktime_tz(struct tm * const tmp, char const * tz);
void localtime_tz(const time_t * const timep, struct tm * tmp, const char* tz);

#ifndef HAVE_ANDROID_OS
/* the following is defined in <time.h> in Bionic */

struct strftime_locale {
    const char *mon[12];    /* short names */
    const char *month[12];  /* long names */
    const char *standalone_month[12];  /* long standalone names */
    const char *wday[7];    /* short names */
    const char *weekday[7]; /* long names */
    const char *X_fmt;
    const char *x_fmt;
    const char *c_fmt;
    const char *am;
    const char *pm;
    const char *date_fmt;
};

size_t strftime_tz(char *s, size_t max, const char *format, const struct tm *tm, const struct strftime_locale *locale);

#endif /* !HAVE_ANDROID_OS */

#ifdef __cplusplus
}
#endif

#endif /* __CUTILS_TZTIME_H */ 

