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

/**
 * A pointer array which intelligently expands its capacity ad needed.
 */

#ifndef __ARRAY_H
#define __ARRAY_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdlib.h>

/** An array. */
typedef struct Array Array;

/** Constructs a new array. Returns NULL if we ran out of memory. */
Array* arrayCreate();

/** Frees an array. Does not free elements themselves. */
void arrayFree(Array* array);

/** Adds a pointer. Returns 0 is successful, < 0 otherwise. */
int arrayAdd(Array* array, void* pointer);

/** Gets the pointer at the specified index. */
void* arrayGet(Array* array, int index);

/** Removes the pointer at the given index and returns it. */
void* arrayRemove(Array* array, int index);

/** Sets pointer at the given index. Returns old pointer. */
void* arraySet(Array* array, int index, void* pointer);

/** Sets the array size. Sets new pointers to NULL. Returns 0 if successful, < 0 otherwise . */
int arraySetSize(Array* array, int size);

/** Returns the size of the given array. */
int arraySize(Array* array);

/** 
 * Returns a pointer to a C-style array which will be valid until this array 
 * changes.
 */
const void** arrayUnwrap(Array* array);

#ifdef __cplusplus
}
#endif

#endif /* __ARRAY_H */ 
