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

/* $Id: SDLnetUDP.c 1192 2004-01-04 17:41:55Z slouken $ */

#include "SDLnetsys.h"
#include "SDL_net.h"
#ifdef MACOS_OPENTRANSPORT
#include <Events.h>
#endif

struct _UDPsocket {
	int ready;
	SOCKET channel;
	IPaddress address;

#ifdef MACOS_OPENTRANSPORT
	OTEventCode newEvent;
	OTEventCode event;
	OTEventCode curEvent;
	OTEventCode newCompletion;
	OTEventCode completion;
	OTEventCode curCompletion;
	TEndpointInfo info;
	Boolean		readShutdown;
	Boolean		writeShutdown;
	OSStatus	error;
	OTConfigurationRef	config;		// Master configuration. you can clone this.
#endif /* MACOS_OPENTRANSPORT */

	struct UDP_channel {
		int numbound;
		IPaddress address[SDLNET_MAX_UDPADDRESSES];
	} binding[SDLNET_MAX_UDPCHANNELS];
};

#ifdef MACOS_OPENTRANSPORT

/* A helper function for Mac OpenTransport support*/
// This function is a complete copy from GUSI
// ( masahiro minami<elsur@aaa.letter.co.jp> )
// ( 01/02/19 )
//
// I guess this function should be put in SDLnet.c
// ( 010315 masahiro minami<elsur@aaa.letter.co.jp>)
// (TODO)
static __inline__ Uint32 CompleteMask(OTEventCode code)	
{ 	
	return 1 << (code & 0x1F); 
}

/* Notifier for async OT calls */
// This function is completely same as AsyncTCPNotifier,
// except for the argument, UDPsocket / TCPsocket
// ( 010315 masahiro minami<elsur@aaa.letter.co.jp>)
static pascal void AsyncUDPNotifier( UDPsocket sock, OTEventCode code,
					OTResult result, void* cookie )
{
	switch( code & 0x7f000000L)
	{
		case 0:
			sock->newEvent |= code;
			result = 0;
			break;
		case kCOMPLETEEVENT:
			if(!(code & 0x00FFFFE0 ))
				sock->newCompletion |= CompleteMask( code );
			if( code == T_OPENCOMPLETE )
				sock->channel = (SOCKET)(cookie);
			break;
		default:
			if( code != kOTProviderWillClose )
				result = 0;
	}
	// Do we need these ???? TODO
	// sock->SetAsyncMacError( result );
	// sock->Wakeup();
	
	// Do we need to ?
	//YieldToAnyThread();
}

/* Retrieve OT event */
// This function is completely same as AsyncTCPPopEvent,
// except for the argument, UDPsocket / TCPsocket
// ( 010315 masahiro minami<elsur@aaa.letter.co.jp>)
static void AsyncUDPPopEvent( UDPsocket sock )
{
	// Make sure OT calls are not interrupted
	// Not sure if we really need this.
	OTEnterNotifier( sock->channel );
	
	sock->event |= (sock->curEvent = sock->newEvent );
	sock->completion |= ( sock->curCompletion = sock->newCompletion );
	sock->newEvent = sock->newCompletion = 0;
	
	OTLeaveNotifier( sock->channel );
	
	if( sock->curEvent & T_UDERR)
	{
		// We just clear the error.
		// Should we feed this back to users ?
		// (TODO )
		OTRcvUDErr( sock->channel, NULL );	
	}
	
	// Remote is disconnecting...
	if( sock->curEvent & ( T_DISCONNECT | T_ORDREL ))
	{
		sock->readShutdown = true;
	}
	
	if( sock->curEvent &T_CONNECT)
	{
		// Ignore the info of remote (second parameter).
		// Shoule we care ?
		// (TODO)
		OTRcvConnect( sock->channel, NULL );	
	}
	
	if( sock->curEvent & T_ORDREL )
	{
		OTRcvOrderlyDisconnect( sock->channel );
	}
	
	if( sock->curEvent & T_DISCONNECT )
	{
		OTRcvDisconnect( sock->channel, NULL );
	}
	
	// Should we ??
	// (010318 masahiro minami<elsur@aaa.letter.co.jp>
	//YieldToAnyThread();
}

/* Create a new UDPsocket */
// Because TCPsocket structure gets bigger and bigger,
// I think we'd better have a constructor function and delete function.
// ( 01/02/25 masahiro minami<elsur@aaa.letter.co.jp> )
/*static*/ UDPsocket AsyncUDPNewSocket()
{
	UDPsocket sock;
	
	sock = (UDPsocket)malloc(sizeof(*sock));
	if ( sock == NULL ) {
		SDLNet_SetError("Out of memory");
		return NULL;
	}
	
	sock->newEvent = 0;
	sock->event = 0;
	sock->curEvent = 0;
	sock->newCompletion = 0;
	sock->completion = 0;
	sock->curCompletion = 0;
	//sock->info = NULL;
	sock->readShutdown = sock->writeShutdown = false;
	sock->error = 0;
	sock->config = NULL;
	
	return sock;	
}

#endif /* MACOS_OPENTRANSPORT */

/* Allocate/free a single UDP packet 'size' bytes long.
   The new packet is returned, or NULL if the function ran out of memory.
 */
extern UDPpacket *SDLNet_AllocPacket(int size)
{
	UDPpacket *packet;
	int error;


	error = 1;
	packet = (UDPpacket *)malloc(sizeof(*packet));
	if ( packet != NULL ) {
		packet->maxlen = size;
		packet->data = (Uint8 *)malloc(size);
		if ( packet->data != NULL ) {
			error = 0;
		}
	}
	if ( error ) {
		SDLNet_FreePacket(packet);
		packet = NULL;
	}
	return(packet);
}
int SDLNet_ResizePacket(UDPpacket *packet, int newsize)
{
	Uint8 *newdata;

	newdata = (Uint8 *)malloc(newsize);
	if ( newdata != NULL ) {
		free(packet->data);
		packet->data = newdata;
		packet->maxlen = newsize;
	}
	return(packet->maxlen);
}
extern void SDLNet_FreePacket(UDPpacket *packet)
{
	if ( packet ) {
		if ( packet->data )
			free(packet->data);
		free(packet);
	}
}

/* Allocate/Free a UDP packet vector (array of packets) of 'howmany' packets,
   each 'size' bytes long.
   A pointer to the packet array is returned, or NULL if the function ran out
   of memory.
 */
UDPpacket **SDLNet_AllocPacketV(int howmany, int size)
{
	UDPpacket **packetV;

	packetV = (UDPpacket **)malloc((howmany+1)*sizeof(*packetV));
	if ( packetV != NULL ) {
		int i;
		for ( i=0; i<howmany; ++i ) {
			packetV[i] = SDLNet_AllocPacket(size);
			if ( packetV[i] == NULL ) {
				break;
			}
		}
		packetV[i] = NULL;

		if ( i != howmany ) {
			SDLNet_FreePacketV(packetV);
			packetV = NULL;
		}
	}
	return(packetV);
}
void SDLNet_FreePacketV(UDPpacket **packetV)
{
	if ( packetV ) {
		int i;
		for ( i=0; packetV[i]; ++i ) {
			SDLNet_FreePacket(packetV[i]);
		}
		free(packetV);
	}
}

/* Since the UNIX/Win32/BeOS code is so different from MacOS,
   we'll just have two completely different sections here.
*/

/* Open a UDP network socket
   If 'port' is non-zero, the UDP socket is bound to a fixed local port.
*/
extern UDPsocket SDLNet_UDP_Open(Uint16 port)
{
	UDPsocket sock;
#ifdef MACOS_OPENTRANSPORT
	EndpointRef dummy = NULL;
#endif

	/* Allocate a UDP socket structure */
	sock = (UDPsocket)malloc(sizeof(*sock));
	if ( sock == NULL ) {
		SDLNet_SetError("Out of memory");
		goto error_return;
	}
	memset(sock, 0, sizeof(*sock));
	
	/* Open the socket */
#ifdef MACOS_OPENTRANSPORT
	{
		sock->error = OTAsyncOpenEndpoint(
			OTCreateConfiguration(kUDPName),0, &(sock->info),
			(OTNotifyProcPtr)AsyncUDPNotifier, sock );
		AsyncUDPPopEvent( sock );
		while( !sock->error && !( sock->completion & CompleteMask(T_OPENCOMPLETE)))
		{
			AsyncUDPPopEvent( sock );
		}
		if( sock->error )
		{
			SDLNet_SetError("Could not open UDP socket");
			goto error_return;
		}
		// Should we ??
		// (01/05/03 minami<elsur@aaa.letter.co.jp>
		OTSetBlocking( sock->channel );
	}
#else
	sock->channel = socket(AF_INET, SOCK_DGRAM, 0);
#endif /* MACOS_OPENTRANSPORT */

	if ( sock->channel == INVALID_SOCKET ) 
	{
		SDLNet_SetError("Couldn't create socket");
		goto error_return;
	}

#ifdef MACOS_OPENTRANSPORT
	{
	InetAddress required, assigned;
	TBind req_addr, assigned_addr;
	OSStatus status;
	InetInterfaceInfo info;
		
		memset(&assigned_addr, 0, sizeof(assigned_addr));
		assigned_addr.addr.maxlen = sizeof(assigned);
		assigned_addr.addr.len = sizeof(assigned);
		assigned_addr.addr.buf = (UInt8 *) &assigned;
		
		if ( port ) {
			status = OTInetGetInterfaceInfo( &info, kDefaultInetInterface );
			if( status != kOTNoError )
				goto error_return;
			OTInitInetAddress(&required, port, info.fAddress );
			req_addr.addr.maxlen = sizeof( required );
			req_addr.addr.len = sizeof( required );
			req_addr.addr.buf = (UInt8 *) &required;
		
			sock->error = OTBind(sock->channel, &req_addr, &assigned_addr);
		} else {
			sock->error = OTBind(sock->channel, nil, &assigned_addr );
		}
		AsyncUDPPopEvent(sock);

		while( !sock->error && !(sock->completion & CompleteMask(T_BINDCOMPLETE)))
		{
			AsyncUDPPopEvent(sock);
		}	
		if (sock->error != noErr)
		{
			SDLNet_SetError("Couldn't bind to local port, OTBind() = %d",(int) status);
			goto error_return;
		}

		sock->address.host = assigned.fHost;
		sock->address.port = assigned.fPort;
		
#ifdef DEBUG_NET
		printf("UDP open host = %d, port = %d\n", assigned.fHost, assigned.fPort );
#endif
	}
#else
	/* Bind locally, if appropriate */
	if ( port )
	{
		struct sockaddr_in sock_addr;
		memset(&sock_addr, 0, sizeof(sock_addr));
		sock_addr.sin_family = AF_INET;
		sock_addr.sin_addr.s_addr = INADDR_ANY;
		sock_addr.sin_port = SDL_SwapBE16(port);

		/* Bind the socket for listening */
		if ( bind(sock->channel, (struct sockaddr *)&sock_addr,
				sizeof(sock_addr)) == SOCKET_ERROR ) {
			SDLNet_SetError("Couldn't bind to local port");
			goto error_return;
		}
		/* Fill in the channel host address */
		sock->address.host = sock_addr.sin_addr.s_addr;
		sock->address.port = sock_addr.sin_port;
	}

#ifdef SO_BROADCAST
	/* Allow LAN broadcasts with the socket */
	{ int yes = 1;
		setsockopt(sock->channel, SOL_SOCKET, SO_BROADCAST, (char*)&yes, sizeof(yes));
	}
#endif
#endif /* MACOS_OPENTRANSPORT */

	/* The socket is ready */
	
	return(sock);

error_return:
#ifdef MACOS_OPENTRANSPORT
	if( dummy )
		OTCloseProvider( dummy );
#endif
	SDLNet_UDP_Close(sock);
	
	return(NULL);
}

/* Verify that the channel is in the valid range */
static int ValidChannel(int channel)
{
	if ( (channel < 0) || (channel >= SDLNET_MAX_UDPCHANNELS) ) {
		SDLNet_SetError("Invalid channel");
		return(0);
	}
	return(1);
}

/* Bind the address 'address' to the requested channel on the UDP socket.
   If the channel is -1, then the first unbound channel will be bound with
   the given address as it's primary address.
   If the channel is already bound, this new address will be added to the
   list of valid source addresses for packets arriving on the channel.
   If the channel is not already bound, then the address becomes the primary
   address, to which all outbound packets on the channel are sent.
   This function returns the channel which was bound, or -1 on error.
*/
int SDLNet_UDP_Bind(UDPsocket sock, int channel, IPaddress *address)
{
	struct UDP_channel *binding;

	if ( channel == -1 ) {
		for ( channel=0; channel < SDLNET_MAX_UDPCHANNELS; ++channel ) {
			binding = &sock->binding[channel];
			if ( binding->numbound < SDLNET_MAX_UDPADDRESSES ) {
				break;
			}
		}
	} else {
		if ( ! ValidChannel(channel) ) {
			return(-1);
		}
		binding = &sock->binding[channel];
	}
	if ( binding->numbound == SDLNET_MAX_UDPADDRESSES ) {
		SDLNet_SetError("No room for new addresses");
		return(-1);
	}
	binding->address[binding->numbound++] = *address;
	return(channel);
}

/* Unbind all addresses from the given channel */
void SDLNet_UDP_Unbind(UDPsocket sock, int channel)
{
	if ( (channel >= 0) && (channel < SDLNET_MAX_UDPCHANNELS) ) {
		sock->binding[channel].numbound = 0;
	}
}

/* Get the primary IP address of the remote system associated with the
   socket and channel.
   If the channel is not bound, this function returns NULL.
 */
IPaddress *SDLNet_UDP_GetPeerAddress(UDPsocket sock, int channel)
{
	IPaddress *address;

	address = NULL;
	switch (channel) {
		case -1:
			/* Return the actual address of the socket */
			address = &sock->address;
			break;
		default:
			/* Return the address of the bound channel */
			if ( ValidChannel(channel) &&
				(sock->binding[channel].numbound > 0) ) {
				address = &sock->binding[channel].address[0];
			}
			break;
	}
	return(address);
}

/* Send a vector of packets to the the channels specified within the packet.
   If the channel specified in the packet is -1, the packet will be sent to
   the address in the 'src' member of the packet.
   Each packet will be updated with the status of the packet after it has 
   been sent, -1 if the packet send failed.
   This function returns the number of packets sent.
*/
int SDLNet_UDP_SendV(UDPsocket sock, UDPpacket **packets, int npackets)
{
	int numsent, i, j;
	struct UDP_channel *binding;
	int status;
#ifndef MACOS_OPENTRANSPORT
	int sock_len;
	struct sockaddr_in sock_addr;

	/* Set up the variables to send packets */
	sock_len = sizeof(sock_addr);
#endif

	numsent = 0;
	for ( i=0; i<npackets; ++i ) 
	{
		/* if channel is < 0, then use channel specified in sock */
		
		if ( packets[i]->channel < 0 ) 
		{
#ifdef MACOS_OPENTRANSPORT
		TUnitData OTpacket;
		InetAddress address;

			memset(&OTpacket, 0, sizeof(OTpacket));
			OTpacket.addr.buf = (Uint8 *)&address;
			OTpacket.addr.len = (sizeof address);
			OTpacket.udata.buf = packets[i]->data;
			OTpacket.udata.len = packets[i]->len;
			OTInitInetAddress(&address, packets[i]->address.port, packets[i]->address.host);
#ifdef DEBUG_NET
			printf("Packet send address: 0x%8.8x:%d, length = %d\n", packets[i]->address.host, packets[i]->address.port, packets[i]->len);
#endif
			
			status = OTSndUData(sock->channel, &OTpacket);
#ifdef DEBUG_NET
			printf("SDLNet_UDP_SendV   OTSndUData return value is ;%d\n", status );
#endif

			AsyncUDPPopEvent( sock );
			packets[i]->status = status;
			
			if (status == noErr)
			{
				++numsent;
			}
#else
			sock_addr.sin_addr.s_addr = packets[i]->address.host;
			sock_addr.sin_port = packets[i]->address.port;
			sock_addr.sin_family = AF_INET;
			status = sendto(sock->channel, 
					packets[i]->data, packets[i]->len, 0,
					(struct sockaddr *)&sock_addr,sock_len);
			if ( status >= 0 )
			{
				packets[i]->status = status;
				++numsent;
			}
#endif /* MACOS_OPENTRANSPORT */
		}
		else 
		{
			/* Send to each of the bound addresses on the channel */
#ifdef DEBUG_NET
			printf("SDLNet_UDP_SendV sending packet to channel = %d\n", packets[i]->channel );
#endif
			
			binding = &sock->binding[packets[i]->channel];
			
			for ( j=binding->numbound-1; j>=0; --j ) 
			{
#ifdef MACOS_OPENTRANSPORT
			TUnitData OTpacket;
			InetAddress address;

				OTInitInetAddress(&address, binding->address[j].port,binding->address[j].host);
#ifdef DEBUG_NET
				printf("Packet send address: 0x%8.8x:%d, length = %d\n", binding->address[j].host, binding->address[j].port, packets[i]->len);
#endif
				memset(&OTpacket, 0, sizeof(OTpacket));
				OTpacket.addr.buf = (Uint8 *)&address;
				OTpacket.addr.len = (sizeof address);
				OTpacket.udata.buf = packets[i]->data;
				OTpacket.udata.len = packets[i]->len;
			                              
				status = OTSndUData(sock->channel, &OTpacket);
#ifdef DEBUG_NET
				printf("SDLNet_UDP_SendV   OTSndUData returne value is;%d\n", status );
#endif
				AsyncUDPPopEvent(sock);
				packets[i]->status = status;
				
				if (status == noErr)
				{
					++numsent;
				}

#else
				sock_addr.sin_addr.s_addr = binding->address[j].host;
				sock_addr.sin_port = binding->address[j].port;
				sock_addr.sin_family = AF_INET;
				status = sendto(sock->channel, 
						packets[i]->data, packets[i]->len, 0,
						(struct sockaddr *)&sock_addr,sock_len);
				if ( status >= 0 )
				{
					packets[i]->status = status;
					++numsent;
				}
#endif /* MACOS_OPENTRANSPORT */
			}
		}
	}
	
	return(numsent);
}

int SDLNet_UDP_Send(UDPsocket sock, int channel, UDPpacket *packet)
{
	/* This is silly, but... */
	packet->channel = channel;
	return(SDLNet_UDP_SendV(sock, &packet, 1));
}

/* Returns true if a socket is has data available for reading right now */
static int SocketReady(SOCKET sock)
{
	int retval = 0;
#ifdef MACOS_OPENTRANSPORT
	OTResult status;
#else
	struct timeval tv;
	fd_set mask;
#endif

#ifdef MACOS_OPENTRANSPORT
	//status = OTGetEndpointState(sock);
	status = OTLook(sock);
	if( status > 0 )
		retval = 1;
		
/*	switch( status )
	{
//		case T_IDLE:
		case T_DATAXFER:
//		case T_INREL:
			retval = 1;
			break;
		default:
			OTCountDataBytes( sock, &numBytes );
			if( numBytes )
				retval = 1;
	}*/
#else
	/* Check the file descriptors for available data */
	do {
		errno = 0;

		/* Set up the mask of file descriptors */
		FD_ZERO(&mask);
		FD_SET(sock, &mask);

		/* Set up the timeout */
		tv.tv_sec = 0;
		tv.tv_usec = 0;

		/* Look! */
		retval = select(sock+1, &mask, NULL, NULL, &tv);
	} while ( errno == EINTR );
#endif /* MACOS_OPENTRANSPORT */

	return(retval == 1);
}

/* Receive a vector of pending packets from the UDP socket.
   The returned packets contain the source address and the channel they arrived
   on.  If they did not arrive on a bound channel, the the channel will be set
   to -1.
   This function returns the number of packets read from the network, or -1
   on error.  This function does not block, so can return 0 packets pending.
*/
extern int SDLNet_UDP_RecvV(UDPsocket sock, UDPpacket **packets)
{
	int numrecv, i, j;
	struct UDP_channel *binding;
#ifdef MACOS_OPENTRANSPORT
	TUnitData OTpacket;
	OTFlags flags;
	InetAddress address;
#else
	int sock_len;
	struct sockaddr_in sock_addr;
#endif

	numrecv = 0;
	while ( packets[numrecv] && SocketReady(sock->channel) ) 
	{
	UDPpacket *packet;

		packet = packets[numrecv];
		
#ifdef MACOS_OPENTRANSPORT
		memset(&OTpacket, 0, sizeof(OTpacket));
		OTpacket.addr.buf = (Uint8 *)&address;
		OTpacket.addr.maxlen = (sizeof address);
		OTpacket.udata.buf = packet->data;
		OTpacket.udata.maxlen = packet->maxlen;
		
		packet->status = OTRcvUData(sock->channel, &OTpacket, &flags);
#ifdef DEBUG_NET
		printf("Packet status: %d\n", packet->status);
#endif
		AsyncUDPPopEvent(sock);
		if (packet->status == noErr)
		{
			packet->len = OTpacket.udata.len;
			packet->address.host = address.fHost;
			packet->address.port = address.fPort;
#ifdef DEBUG_NET
			printf("Packet address: 0x%8.8x:%d, length = %d\n", packet->address.host, packet->address.port, packet->len);
#endif
		}
#else
		sock_len = sizeof(sock_addr);
		packet->status = recvfrom(sock->channel,
				packet->data, packet->maxlen, 0,
				(struct sockaddr *)&sock_addr,
#ifdef USE_GUSI_SOCKETS
				(unsigned int *)&sock_len);
#else
						&sock_len);
#endif
		if ( packet->status >= 0 ) {
			packet->len = packet->status;
			packet->address.host = sock_addr.sin_addr.s_addr;
			packet->address.port = sock_addr.sin_port;
		}
#endif
		if (packet->status >= 0)
		{
			packet->channel = -1;
			
			for (i=(SDLNET_MAX_UDPCHANNELS-1); i>=0; --i ) 
			{
				binding = &sock->binding[i];
				
				for ( j=binding->numbound-1; j>=0; --j ) 
				{
					if ( (packet->address.host == binding->address[j].host) &&
					     (packet->address.port == binding->address[j].port) ) 
					{
						packet->channel = i;
						goto foundit; /* break twice */
					}
				}
			}
foundit:
			++numrecv;
		} 
		
		else 
		{
			packet->len = 0;
		}
	}
	
	sock->ready = 0;
	
	return(numrecv);
}

/* Receive a single packet from the UDP socket.
   The returned packet contains the source address and the channel it arrived
   on.  If it did not arrive on a bound channel, the the channel will be set
   to -1.
   This function returns the number of packets read from the network, or -1
   on error.  This function does not block, so can return 0 packets pending.
*/
int SDLNet_UDP_Recv(UDPsocket sock, UDPpacket *packet)
{
	UDPpacket *packets[2];

	/* Receive a packet array of 1 */
	packets[0] = packet;
	packets[1] = NULL;
	return(SDLNet_UDP_RecvV(sock, packets));
}

/* Close a UDP network socket */
extern void SDLNet_UDP_Close(UDPsocket sock)
{
	if ( sock != NULL ) 
	{
		if ( sock->channel != INVALID_SOCKET ) 
		{
#ifdef MACOS_OPENTRANSPORT
			OTUnbind(sock->channel);
			OTCloseProvider(sock->channel);
#else
			closesocket(sock->channel);
#endif /* MACOS_OPENTRANSPORT */
		}
		
		free(sock);
	}
}

