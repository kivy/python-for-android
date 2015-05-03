/*
    SDL_net:  An example cross-platform network library for use with SDL
    Copyright (C) 1997-2004 Sam Lantinga

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.

    You should have received a copy of the GNU Library General Public
    License along with this library; if not, write to the Free
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

    Sam Lantinga
    slouken@libsdl.org
*/

/* $Id: SDL_net.h 3281 2007-07-15 05:58:56Z slouken $ */

#ifndef _SDL_NET_H
#define _SDL_NET_H

#include "SDL.h"
#include "SDL_endian.h"
#include "SDL_version.h"
#include "begin_code.h"



/* Set up for C function definitions, even when using C++ */
#ifdef __cplusplus
extern "C" {
#endif

/* Printable format: "%d.%d.%d", MAJOR, MINOR, PATCHLEVEL
*/
#define SDL_NET_MAJOR_VERSION	1
#define SDL_NET_MINOR_VERSION	2
#define SDL_NET_PATCHLEVEL	7

/* This macro can be used to fill a version structure with the compile-time
 * version of the SDL_net library.
 */
#define SDL_NET_VERSION(X)						\
{									\
	(X)->major = SDL_NET_MAJOR_VERSION;				\
	(X)->minor = SDL_NET_MINOR_VERSION;				\
	(X)->patch = SDL_NET_PATCHLEVEL;				\
}

/* This function gets the version of the dynamically linked SDL_net library.
   it should NOT be used to fill a version structure, instead you should
   use the SDL_NET_VERSION() macro.
 */
extern DECLSPEC const SDL_version * SDLCALL SDLNet_Linked_Version(void);

/* Initialize/Cleanup the network API
   SDL must be initialized before calls to functions in this library,
   because this library uses utility functions from the SDL library.
*/
extern DECLSPEC int  SDLCALL SDLNet_Init(void);
extern DECLSPEC void SDLCALL SDLNet_Quit(void);

/***********************************************************************/
/* IPv4 hostname resolution API                                        */
/***********************************************************************/

typedef struct {
	Uint32 host;			/* 32-bit IPv4 host address */
	Uint16 port;			/* 16-bit protocol port */
} IPaddress;

/* Resolve a host name and port to an IP address in network form.
   If the function succeeds, it will return 0.
   If the host couldn't be resolved, the host portion of the returned
   address will be INADDR_NONE, and the function will return -1.
   If 'host' is NULL, the resolved host will be set to INADDR_ANY.
 */
#ifndef INADDR_ANY
#define INADDR_ANY		0x00000000
#endif
#ifndef INADDR_NONE
#define INADDR_NONE		0xFFFFFFFF
#endif
#ifndef INADDR_BROADCAST
#define INADDR_BROADCAST	0xFFFFFFFF
#endif
extern DECLSPEC int SDLCALL SDLNet_ResolveHost(IPaddress *address, const char *host, Uint16 port);

/* Resolve an ip address to a host name in canonical form.
   If the ip couldn't be resolved, this function returns NULL,
   otherwise a pointer to a static buffer containing the hostname
   is returned.  Note that this function is not thread-safe.
*/
extern DECLSPEC const char * SDLCALL SDLNet_ResolveIP(IPaddress *ip);


/***********************************************************************/
/* TCP network API                                                     */
/***********************************************************************/

typedef struct _TCPsocket *TCPsocket;

/* Open a TCP network socket
   If ip.host is INADDR_NONE or INADDR_ANY, this creates a local server
   socket on the given port, otherwise a TCP connection to the remote
   host and port is attempted. The address passed in should already be
   swapped to network byte order (addresses returned from 
   SDLNet_ResolveHost() are already in the correct form).
   The newly created socket is returned, or NULL if there was an error.
*/
extern DECLSPEC TCPsocket SDLCALL SDLNet_TCP_Open(IPaddress *ip);

/* Accept an incoming connection on the given server socket.
   The newly created socket is returned, or NULL if there was an error.
*/
extern DECLSPEC TCPsocket SDLCALL SDLNet_TCP_Accept(TCPsocket server);

/* Get the IP address of the remote system associated with the socket.
   If the socket is a server socket, this function returns NULL.
*/
extern DECLSPEC IPaddress * SDLCALL SDLNet_TCP_GetPeerAddress(TCPsocket sock);

/* Send 'len' bytes of 'data' over the non-server socket 'sock'
   This function returns the actual amount of data sent.  If the return value
   is less than the amount of data sent, then either the remote connection was
   closed, or an unknown socket error occurred.
*/
extern DECLSPEC int SDLCALL SDLNet_TCP_Send(TCPsocket sock, const void *data,
		int len);

/* Receive up to 'maxlen' bytes of data over the non-server socket 'sock',
   and store them in the buffer pointed to by 'data'.
   This function returns the actual amount of data received.  If the return
   value is less than or equal to zero, then either the remote connection was
   closed, or an unknown socket error occurred.
*/
extern DECLSPEC int SDLCALL SDLNet_TCP_Recv(TCPsocket sock, void *data, int maxlen);

/* Close a TCP network socket */
extern DECLSPEC void SDLCALL SDLNet_TCP_Close(TCPsocket sock);


/***********************************************************************/
/* UDP network API                                                     */
/***********************************************************************/

/* The maximum channels on a a UDP socket */
#define SDLNET_MAX_UDPCHANNELS	32
/* The maximum addresses bound to a single UDP socket channel */
#define SDLNET_MAX_UDPADDRESSES	4

typedef struct _UDPsocket *UDPsocket;
typedef struct {
	int channel;		/* The src/dst channel of the packet */
	Uint8 *data;		/* The packet data */
	int len;		/* The length of the packet data */
	int maxlen;		/* The size of the data buffer */
	int status;		/* packet status after sending */
	IPaddress address;		/* The source/dest address of an incoming/outgoing packet */
} UDPpacket;

/* Allocate/resize/free a single UDP packet 'size' bytes long.
   The new packet is returned, or NULL if the function ran out of memory.
 */
extern DECLSPEC UDPpacket * SDLCALL SDLNet_AllocPacket(int size);
extern DECLSPEC int SDLCALL SDLNet_ResizePacket(UDPpacket *packet, int newsize);
extern DECLSPEC void SDLCALL SDLNet_FreePacket(UDPpacket *packet);

/* Allocate/Free a UDP packet vector (array of packets) of 'howmany' packets,
   each 'size' bytes long.
   A pointer to the first packet in the array is returned, or NULL if the
   function ran out of memory.
 */
extern DECLSPEC UDPpacket ** SDLCALL SDLNet_AllocPacketV(int howmany, int size);
extern DECLSPEC void SDLCALL SDLNet_FreePacketV(UDPpacket **packetV);


/* Open a UDP network socket
   If 'port' is non-zero, the UDP socket is bound to a local port.
   The 'port' should be given in native byte order, but is used
   internally in network (big endian) byte order, in addresses, etc.
   This allows other systems to send to this socket via a known port.
*/
extern DECLSPEC UDPsocket SDLCALL SDLNet_UDP_Open(Uint16 port);

/* Bind the address 'address' to the requested channel on the UDP socket.
   If the channel is -1, then the first unbound channel will be bound with
   the given address as it's primary address.
   If the channel is already bound, this new address will be added to the
   list of valid source addresses for packets arriving on the channel.
   If the channel is not already bound, then the address becomes the primary
   address, to which all outbound packets on the channel are sent.
   This function returns the channel which was bound, or -1 on error.
*/
extern DECLSPEC int SDLCALL SDLNet_UDP_Bind(UDPsocket sock, int channel, IPaddress *address);

/* Unbind all addresses from the given channel */
extern DECLSPEC void SDLCALL SDLNet_UDP_Unbind(UDPsocket sock, int channel);

/* Get the primary IP address of the remote system associated with the 
   socket and channel.  If the channel is -1, then the primary IP port
   of the UDP socket is returned -- this is only meaningful for sockets
   opened with a specific port.
   If the channel is not bound and not -1, this function returns NULL.
 */
extern DECLSPEC IPaddress * SDLCALL SDLNet_UDP_GetPeerAddress(UDPsocket sock, int channel);

/* Send a vector of packets to the the channels specified within the packet.
   If the channel specified in the packet is -1, the packet will be sent to
   the address in the 'src' member of the packet.
   Each packet will be updated with the status of the packet after it has 
   been sent, -1 if the packet send failed.
   This function returns the number of packets sent.
*/
extern DECLSPEC int SDLCALL SDLNet_UDP_SendV(UDPsocket sock, UDPpacket **packets, int npackets);

/* Send a single packet to the specified channel.
   If the channel specified in the packet is -1, the packet will be sent to
   the address in the 'src' member of the packet.
   The packet will be updated with the status of the packet after it has
   been sent.
   This function returns 1 if the packet was sent, or 0 on error.

   NOTE:
   The maximum size of the packet is limited by the MTU (Maximum Transfer Unit)
   of the transport medium.  It can be as low as 250 bytes for some PPP links,
   and as high as 1500 bytes for ethernet.
*/
extern DECLSPEC int SDLCALL SDLNet_UDP_Send(UDPsocket sock, int channel, UDPpacket *packet);

/* Receive a vector of pending packets from the UDP socket.
   The returned packets contain the source address and the channel they arrived
   on.  If they did not arrive on a bound channel, the the channel will be set
   to -1.
   The channels are checked in highest to lowest order, so if an address is
   bound to multiple channels, the highest channel with the source address
   bound will be returned.
   This function returns the number of packets read from the network, or -1
   on error.  This function does not block, so can return 0 packets pending.
*/
extern DECLSPEC int SDLCALL SDLNet_UDP_RecvV(UDPsocket sock, UDPpacket **packets);

/* Receive a single packet from the UDP socket.
   The returned packet contains the source address and the channel it arrived
   on.  If it did not arrive on a bound channel, the the channel will be set
   to -1.
   The channels are checked in highest to lowest order, so if an address is
   bound to multiple channels, the highest channel with the source address
   bound will be returned.
   This function returns the number of packets read from the network, or -1
   on error.  This function does not block, so can return 0 packets pending.
*/
extern DECLSPEC int SDLCALL SDLNet_UDP_Recv(UDPsocket sock, UDPpacket *packet);

/* Close a UDP network socket */
extern DECLSPEC void SDLCALL SDLNet_UDP_Close(UDPsocket sock);


/***********************************************************************/
/* Hooks for checking sockets for available data                       */
/***********************************************************************/

typedef struct _SDLNet_SocketSet *SDLNet_SocketSet;

/* Any network socket can be safely cast to this socket type */
typedef struct {
	int ready;
} *SDLNet_GenericSocket;

/* Allocate a socket set for use with SDLNet_CheckSockets()
   This returns a socket set for up to 'maxsockets' sockets, or NULL if
   the function ran out of memory.
 */
extern DECLSPEC SDLNet_SocketSet SDLCALL SDLNet_AllocSocketSet(int maxsockets);

/* Add a socket to a set of sockets to be checked for available data */
#define SDLNet_TCP_AddSocket(set, sock) \
			SDLNet_AddSocket(set, (SDLNet_GenericSocket)sock)
#define SDLNet_UDP_AddSocket(set, sock) \
			SDLNet_AddSocket(set, (SDLNet_GenericSocket)sock)
extern DECLSPEC int SDLCALL SDLNet_AddSocket(SDLNet_SocketSet set, SDLNet_GenericSocket sock);

/* Remove a socket from a set of sockets to be checked for available data */
#define SDLNet_TCP_DelSocket(set, sock) \
			SDLNet_DelSocket(set, (SDLNet_GenericSocket)sock)
#define SDLNet_UDP_DelSocket(set, sock) \
			SDLNet_DelSocket(set, (SDLNet_GenericSocket)sock)
extern DECLSPEC int SDLCALL SDLNet_DelSocket(SDLNet_SocketSet set, SDLNet_GenericSocket sock);

/* This function checks to see if data is available for reading on the
   given set of sockets.  If 'timeout' is 0, it performs a quick poll,
   otherwise the function returns when either data is available for
   reading, or the timeout in milliseconds has elapsed, which ever occurs
   first.  This function returns the number of sockets ready for reading, 
   or -1 if there was an error with the select() system call.
*/
extern DECLSPEC int SDLCALL SDLNet_CheckSockets(SDLNet_SocketSet set, Uint32 timeout);

/* After calling SDLNet_CheckSockets(), you can use this function on a
   socket that was in the socket set, to find out if data is available
   for reading.
*/
#define SDLNet_SocketReady(sock) \
		((sock != NULL) && ((SDLNet_GenericSocket)sock)->ready)

/* Free a set of sockets allocated by SDL_NetAllocSocketSet() */
extern DECLSPEC void SDLCALL SDLNet_FreeSocketSet(SDLNet_SocketSet set);


/***********************************************************************/
/* Platform-independent data conversion functions                      */
/***********************************************************************/

/* Write a 16/32 bit value to network packet buffer */
extern DECLSPEC void SDLCALL SDLNet_Write16(Uint16 value, void *area);
extern DECLSPEC void SDLCALL SDLNet_Write32(Uint32 value, void *area);

/* Read a 16/32 bit value from network packet buffer */
extern DECLSPEC Uint16 SDLCALL SDLNet_Read16(void *area);
extern DECLSPEC Uint32 SDLCALL SDLNet_Read32(void *area);

/***********************************************************************/
/* Error reporting functions                                           */
/***********************************************************************/

/* We'll use SDL's functions for error reporting */
#define SDLNet_SetError	SDL_SetError
#define SDLNet_GetError	SDL_GetError

/* I'm eventually going to try to disentangle SDL_net from SDL, thus making
   SDL_net an independent X-platform networking toolkit.  Not today though....

extern no_parse_DECLSPEC void SDLCALL SDLNet_SetError(const char *fmt, ...);
extern no_parse_DECLSPEC char * SDLCALL SDLNet_GetError(void);
*/


/* Inline macro functions to read/write network data */

/* Warning, some systems have data access alignment restrictions */
#if defined(sparc) || defined(mips)
#define SDL_DATA_ALIGNED	1
#endif
#ifndef SDL_DATA_ALIGNED
#define SDL_DATA_ALIGNED	0
#endif

/* Write a 16 bit value to network packet buffer */
#if !SDL_DATA_ALIGNED
#define SDLNet_Write16(value, areap)	\
	(*(Uint16 *)(areap) = SDL_SwapBE16(value))
#else
#if SDL_BYTEORDER == SDL_BIG_ENDIAN
#define SDLNet_Write16(value, areap)	\
do 					\
{					\
	Uint8 *area = (Uint8 *)(areap);	\
	area[0] = (value >>  8) & 0xFF;	\
	area[1] =  value        & 0xFF;	\
} while ( 0 )
#else
#define SDLNet_Write16(value, areap)	\
do 					\
{					\
	Uint8 *area = (Uint8 *)(areap);	\
	area[1] = (value >>  8) & 0xFF;	\
	area[0] =  value        & 0xFF;	\
} while ( 0 )
#endif
#endif /* !SDL_DATA_ALIGNED */

/* Write a 32 bit value to network packet buffer */
#if !SDL_DATA_ALIGNED
#define SDLNet_Write32(value, areap) 	\
	*(Uint32 *)(areap) = SDL_SwapBE32(value);
#else
#if SDL_BYTEORDER == SDL_BIG_ENDIAN
#define SDLNet_Write32(value, areap) 	\
do					\
{					\
	Uint8 *area = (Uint8 *)(areap);	\
	area[0] = (value >> 24) & 0xFF;	\
	area[1] = (value >> 16) & 0xFF;	\
	area[2] = (value >>  8) & 0xFF;	\
	area[3] =  value       & 0xFF;	\
} while ( 0 )
#else
#define SDLNet_Write32(value, areap) 	\
do					\
{					\
	Uint8 *area = (Uint8 *)(areap);	\
	area[3] = (value >> 24) & 0xFF;	\
	area[2] = (value >> 16) & 0xFF;	\
	area[1] = (value >>  8) & 0xFF;	\
	area[0] =  value       & 0xFF;	\
} while ( 0 )
#endif
#endif /* !SDL_DATA_ALIGNED */

/* Read a 16 bit value from network packet buffer */
#if !SDL_DATA_ALIGNED
#define SDLNet_Read16(areap) 		\
	(SDL_SwapBE16(*(Uint16 *)(areap)))
#else
#if SDL_BYTEORDER == SDL_BIG_ENDIAN
#define SDLNet_Read16(areap) 		\
	((((Uint8 *)areap)[0] <<  8) | ((Uint8 *)areap)[1] <<  0)
#else
#define SDLNet_Read16(areap) 		\
	((((Uint8 *)areap)[1] <<  8) | ((Uint8 *)areap)[0] <<  0)
#endif
#endif /* !SDL_DATA_ALIGNED */

/* Read a 32 bit value from network packet buffer */
#if !SDL_DATA_ALIGNED
#define SDLNet_Read32(areap) 		\
	(SDL_SwapBE32(*(Uint32 *)(areap)))
#else
#if SDL_BYTEORDER == SDL_BIG_ENDIAN
#define SDLNet_Read32(areap) 		\
	((((Uint8 *)areap)[0] << 24) | (((Uint8 *)areap)[1] << 16) | \
	 (((Uint8 *)areap)[2] <<  8) |  ((Uint8 *)areap)[3] <<  0)
#else
#define SDLNet_Read32(areap) 		\
	((((Uint8 *)areap)[3] << 24) | (((Uint8 *)areap)[2] << 16) | \
	 (((Uint8 *)areap)[1] <<  8) |  ((Uint8 *)areap)[0] <<  0)
#endif
#endif /* !SDL_DATA_ALIGNED */

#ifdef MACOS_OPENTRANSPORT
#endif
/* Ends C function definitions when using C++ */
#ifdef __cplusplus
}
#endif
#include "close_code.h"

#endif /* _SDL_NET_H */
