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

/* A wrapper file for dlmalloc.h that defines prototypes for the
 * mspace_*() functions, which provide an interface for creating
 * multiple heaps.
 */

#ifndef MSPACE_H_
#define MSPACE_H_

/* It's a pain getting the mallinfo stuff to work
 * with Linux, OSX, and klibc, so just turn it off
 * for now.
 * TODO: make mallinfo work
 */
#define NO_MALLINFO 1

/* Allow setting the maximum heap footprint.
 */
#define USE_MAX_ALLOWED_FOOTPRINT 1

#define USE_CONTIGUOUS_MSPACES 1
#if USE_CONTIGUOUS_MSPACES
#define HAVE_MMAP 0
#define HAVE_MORECORE 1
#define MORECORE_CONTIGUOUS 0
#endif

#define MSPACES 1
#define ONLY_MSPACES 1
#include "../bionic/libc/bionic/dlmalloc.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
  mspace_usable_size(void* p);

  Returns the number of bytes you can actually use in
  an allocated chunk, which may be more than you requested (although
  often not) due to alignment and minimum size constraints.
  You can use this many bytes without worrying about
  overwriting other allocated objects. This is not a particularly great
  programming practice. mspace_usable_size can be more useful in
  debugging and assertions, for example:

  p = mspace_malloc(msp, n);
  assert(mspace_usable_size(msp, p) >= 256);
*/
size_t mspace_usable_size(mspace, const void*);

#if USE_CONTIGUOUS_MSPACES
/*
  Similar to create_mspace(), but the underlying memory is
  guaranteed to be contiguous.  No more than max_capacity
  bytes is ever allocated to the mspace.
 */
mspace create_contiguous_mspace(size_t starting_capacity, size_t max_capacity,
    int locked);

/*
   Identical to create_contiguous_mspace, but labels the mapping 'mspace/name'
   instead of 'mspace'
*/
mspace create_contiguous_mspace_with_name(size_t starting_capacity,
    size_t max_capacity, int locked, const char *name);

size_t destroy_contiguous_mspace(mspace msp);
#endif

/*
  Call the handler for each block in the specified mspace.
  chunkptr and chunklen refer to the heap-level chunk including
  the chunk overhead, and userptr and userlen refer to the
  user-usable part of the chunk.  If the chunk is free, userptr
  will be NULL and userlen will be 0.  userlen is not guaranteed
  to be the same value passed into malloc() for a given chunk;
  it is >= the requested size.
 */
void mspace_walk_heap(mspace msp,
    void(*handler)(const void *chunkptr, size_t chunklen,
        const void *userptr, size_t userlen, void *arg), void *harg);

/*
  mspace_walk_free_pages(handler, harg)

  Calls the provided handler on each free region in the specified
  mspace.  The memory between start and end are guaranteed not to
  contain any important data, so the handler is free to alter the
  contents in any way.  This can be used to advise the OS that large
  free regions may be swapped out.

  The value in harg will be passed to each call of the handler.
 */
void mspace_walk_free_pages(mspace msp,
    void(*handler)(void *start, void *end, void *arg), void *harg);

#ifdef __cplusplus
};  /* end of extern "C" */
#endif

#endif /* MSPACE_H_ */
