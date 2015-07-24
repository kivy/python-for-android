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
 * IPC messaging library.
 */

#ifndef __MQ_H
#define __MQ_H

#ifdef __cplusplus
extern "C" {
#endif

/** A message. */
typedef struct MqMessage MqMessage;

/** A destination to which messages can be sent. */
typedef struct MqDestination MqDestination;

/* Array of bytes. */
typedef struct MqBytes MqBytes;

/** 
 * Hears messages. 
 * 
 * @param destination to which the message was sent
 * @param message the message to hear
 */
typedef void MqMessageListener(MqDestination* destination, MqMessage* message);

/** 
 * Hears a destination close.
 * 
 * @param destination that closed
 */
typedef void MqCloseListener(MqDestination* destination);

/** Message functions. */

/** 
 * Creates a new Message.
 * 
 * @param header as defined by user
 * @param body as defined by user
 * @param replyTo destination to which replies should be sent, NULL if none
 */
MqMessage* mqCreateMessage(MqBytes header, MqBytes body, 
        MqDestination* replyTo);

/** Sends a message to a destination. */
void mqSendMessage(MqMessage* message, MqDestination* destination);

/** Destination functions. */

/** 
 * Creates a new destination. Acquires a reference implicitly.
 *
 * @param messageListener function to call when a message is recieved
 * @param closeListener function to call when the destination closes
 * @param userData user-specific data to associate with the destination.
 *  Retrieve using mqGetDestinationUserData().
 */
MqDestination* mqCreateDestination(MqMessageListener* messageListener, 
        MqCloseListener* closeListener, void* userData);

/**
 * Gets user data which was associated with the given destination at 
 * construction time. 
 * 
 * It is only valid to call this function in the same process that the 
 * given destination was created in.
 * This function returns a null pointer if you call it on a destination
 * created in a remote process.
 */
void* mqGetUserData(MqDestination* destination);

/**
 * Returns 1 if the destination was created in this process, or 0 if
 * the destination was created in a different process, in which case you have
 * a remote stub.
 */
int mqIsDestinationLocal(MqDestination* destination);

/**
 * Increments the destination's reference count.
 */
void mqKeepDestination(MqDesintation* destination);

/**
 * Decrements the destination's reference count. 
 */
void mqFreeDestination(MqDestination* desintation);

/** Registry API. */

/**
 * Gets the destination bound to a name.
 */
MqDestination* mqGetDestination(char* name);

/**
 * Binds a destination to a name.
 */
void mqPutDestination(char* name, MqDestination* desintation);

#ifdef __cplusplus
}
#endif

#endif /* __MQ_H */ 
