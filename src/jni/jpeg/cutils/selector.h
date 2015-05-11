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
 * Framework for multiplexing I/O. A selector manages a set of file
 * descriptors and calls out to user-provided callback functions to read and
 * write data and handle errors.
 */

#ifndef __SELECTOR_H
#define __SELECTOR_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdbool.h>
    
/** 
 * Manages SelectableFds and invokes their callbacks at appropriate times. 
 */
typedef struct Selector Selector;

/** 
 * A selectable descriptor. Contains callbacks which the selector can invoke
 * before calling select(), when the descriptor is readable or writable, and 
 * when the descriptor contains out-of-band data. Simply set a callback to 
 * NULL if you're not interested in that particular event.
 *
 * A selectable descriptor can indicate that it needs to be removed from the
 * selector by setting the 'remove' flag. The selector will remove the
 * descriptor at a later time and invoke the onRemove() callback.
 * 
 * SelectableFd fields should only be modified from the selector loop.
 */
typedef struct SelectableFd SelectableFd;
struct SelectableFd {

    /** The file descriptor itself. */
    int fd;
    
    /** Pointer to user-specific data. Can be NULL. */
    void* data;
    
    /** 
     * Set this flag when you no longer wish to be selected. The selector
     * will invoke onRemove() when the descriptor is actually removed.
     */
    bool remove;

    /** 
     * Invoked by the selector before calling select. You can set up other
     * callbacks from here as necessary.
     */
    void (*beforeSelect)(SelectableFd* self);

    /** 
     * Invoked by the selector when the descriptor has data available. Set to
     * NULL to indicate that you're not interested in reading.
     */
    void (*onReadable)(SelectableFd* self);

    /** 
     * Invoked by the selector when the descriptor can accept data. Set to
     * NULL to indicate that you're not interested in writing.
     */
    void (*onWritable)(SelectableFd* self);

    /** 
     * Invoked by the selector when out-of-band (OOB) data is available. Set to
     * NULL to indicate that you're not interested in OOB data.
     */
    void (*onExcept)(SelectableFd* self);

    /**
     * Invoked by the selector after the descriptor is removed from the
     * selector but before the selector frees the SelectableFd memory.
     */
    void (*onRemove)(SelectableFd* self);

    /**
     * The selector which selected this fd. Set by the selector itself.
     */
    Selector* selector;
};

/** 
 * Creates a new selector. 
 */
Selector* selectorCreate(void);

/** 
 * Creates a new selectable fd, adds it to the given selector and returns a 
 * pointer. Outside of 'selector' and 'fd', all fields are set to 0 or NULL 
 * by default.
 * 
 * The selectable fd should only be modified from the selector loop thread.
 */
SelectableFd* selectorAdd(Selector* selector, int fd);

/**
 * Wakes up the selector even though no I/O events occurred. Use this
 * to indicate that you're ready to write to a descriptor.
 */
void selectorWakeUp(Selector* selector);
    
/** 
 * Loops continuously selecting file descriptors and firing events. 
 * Does not return. 
 */
void selectorLoop(Selector* selector);

#ifdef __cplusplus
}
#endif

#endif /* __SELECTOR_H */ 
