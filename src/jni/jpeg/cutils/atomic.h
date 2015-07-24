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

#ifndef ANDROID_CUTILS_ATOMIC_H
#define ANDROID_CUTILS_ATOMIC_H

#include <stdint.h>
#include <sys/types.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * NOTE: memory shared between threads is synchronized by all atomic operations
 * below, this means that no explicit memory barrier is required: all reads or 
 * writes issued before android_atomic_* operations are guaranteed to complete
 * before the atomic operation takes place.
 */

void android_atomic_write(int32_t value, volatile int32_t* addr);

/*
 * all these atomic operations return the previous value
 */


int32_t android_atomic_inc(volatile int32_t* addr);
int32_t android_atomic_dec(volatile int32_t* addr);

int32_t android_atomic_add(int32_t value, volatile int32_t* addr);
int32_t android_atomic_and(int32_t value, volatile int32_t* addr);
int32_t android_atomic_or(int32_t value, volatile int32_t* addr);

int32_t android_atomic_swap(int32_t value, volatile int32_t* addr);

/*
 * NOTE: Two "quasiatomic" operations on the exact same memory address
 * are guaranteed to operate atomically with respect to each other,
 * but no guarantees are made about quasiatomic operations mixed with
 * non-quasiatomic operations on the same address, nor about
 * quasiatomic operations that are performed on partially-overlapping
 * memory.
 */

int64_t android_quasiatomic_swap_64(int64_t value, volatile int64_t* addr);
int64_t android_quasiatomic_read_64(volatile int64_t* addr);
    
/*
 * cmpxchg return a non zero value if the exchange was NOT performed,
 * in other words if oldvalue != *addr
 */

int android_atomic_cmpxchg(int32_t oldvalue, int32_t newvalue,
        volatile int32_t* addr);

int android_quasiatomic_cmpxchg_64(int64_t oldvalue, int64_t newvalue,
        volatile int64_t* addr);


    
#ifdef __cplusplus
} // extern "C"
#endif

#endif // ANDROID_CUTILS_ATOMIC_H
