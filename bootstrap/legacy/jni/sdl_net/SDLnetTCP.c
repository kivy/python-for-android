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

/* $Id: SDLnetTCP.c 3280 2007-07-15 05:55:42Z slouken $ */

#include "SDLnetsys.h"
#include "SDL_net.h"

/* The network API for TCP sockets */

/* Since the UNIX/Win32/BeOS code is so different from MacOS,
   we'll just have two completely different sections here.
*/

#ifdef MACOS_OPENTRANSPORT

#include <Events.h>
#include <Threads.h>
#include <OpenTransport.h>
#include <OpenTptInternet.h>
#include <OTDebug.h>

struct _TCPsocket {
	int ready;
	SOCKET channel;
	
	// These are taken from GUSI interface.
	// I'm not sure if it's really necessary here yet
	// ( masahiro minami<elsur@aaa.letter.co.jp> )
	// ( 01/02/19 )
	OTEventCode curEvent;
	OTEventCode newEvent;
	OTEventCode event;
	OTEventCode curCompletion;
	OTEventCode newCompletion;
	OTEventCode completion;
	OSStatus	error;
	TEndpointInfo info;
	Boolean		readShutdown;
	Boolean		writeShutdown;
	Boolean		connected;
	OTConfigurationRef	config;		// Master configuration. you can clone this.
	TCPsocket	nextListener;
	// ( end of new members --- masahiro minami<elsur@aaa.letter.co.jp>
	
	IPaddress remoteAddress;
	IPaddress localAddress;
	int sflag;
	
	// Maybe we don't need this---- it's from original SDL_net
	// (masahiro minami<elsur@aaa.letter.co.jp>)
	// ( 01/02/20 )
	int rcvdPassConn;
};

// To be used in WaitNextEvent() here and there....
// (010311 masahiro minami<elsur@aaa.letter.co.jp>)
EventRecord macEvent;

#if TARGET_API_MAC_CARBON
/* for Carbon */
OTNotifyUPP notifier;
#endif

/* Input: ep - endpointref on which to negotiate the option
			enableReuseIPMode - desired option setting - true/false
   Return: kOTNoError indicates that the option was successfully negotiated
   			OSStatus is an error if < 0, otherwise, the status field is
   			returned and is > 0.
   	
   	IMPORTANT NOTE: The endpoint is assumed to be in synchronous more, otherwise
   			this code will not function as desired
*/

/*
NOTE: As this version is written async way, we don't use this function...
(010526) masahiro minami<elsur@aaa.letter.co.jp>
*/
/*
OSStatus DoNegotiateIPReuseAddrOption(EndpointRef ep, Boolean enableReuseIPMode)

{
	UInt8		buf[kOTFourByteOptionSize];	// define buffer for fourByte Option size
	TOption*	opt;						// option ptr to make items easier to access
	TOptMgmt	req;
	TOptMgmt	ret;
	OSStatus	err;
	
	if (!OTIsSynchronous(ep))
	{
		return (-1);
	}
	opt = (TOption*)buf;					// set option ptr to buffer
	req.opt.buf	= buf;
	req.opt.len	= sizeof(buf);
	req.flags	= T_NEGOTIATE;				// negotiate for option

	ret.opt.buf = buf;
	ret.opt.maxlen = kOTFourByteOptionSize;

	opt->level	= INET_IP;					// dealing with an IP Level function
	opt->name	= IP_REUSEADDR;
	opt->len	= kOTFourByteOptionSize;
	opt->status = 0;
	*(UInt32*)opt->value = enableReuseIPMode;		// set the desired option level, true or false

	err = OTOptionManagement(ep, &req, &ret);
	
		// if no error then return the option status value
	if (err == kOTNoError)
	{
		if (opt->status != T_SUCCESS)
			err = opt->status;
		else
			err = kOTNoError;
	}
				
	return err;
}
*/

/* A helper function for Mac OpenTransport support*/
// This function is a complete copy from GUSI
// ( masahiro minami<elsur@aaa.letter.co.jp> )
// ( 01/02/19 )
static __inline__ Uint32 CompleteMask(OTEventCode code)	
{ 	
	return 1 << (code & 0x1F);
}

/* Notifier for async OT calls */
static pascal void AsyncTCPNotifier( TCPsocket sock, OTEventCode code,
					OTResult result, void* cookie )
{

#ifdef DEBUG_NET
	printf("AsyncTCPNotifier got an event : 0x%8.8x\n", code );
#endif
	
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
}

/* Retrieve OT event */
// This function is taken from GUSI interface.
// ( 01/02/19 masahiro minami<elsur@aaa.letter.co.jp> )
static void AsyncTCPPopEvent( TCPsocket sock )
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
		
#ifdef DEBUG_NET
		printf("AsyncTCPPopEvent  T_UDERR recognized");
#endif
	}
	
	// Remote is disconnecting...
	if( sock->curEvent & ( T_DISCONNECT | T_ORDREL ))
	{
		sock->readShutdown = true;
	}
	
	if( sock->curEvent &T_CONNECT )
	{
		// Ignore the info of remote (second parameter).
		// Shoule we care ?
		// (TODO)
		OTRcvConnect( sock->channel, NULL );
		sock->connected = 1;
	}
	
	if( sock->curEvent & T_ORDREL )
	{
		OTRcvOrderlyDisconnect( sock->channel );
	}
	
	if( sock->curEvent & T_DISCONNECT )
	{
		OTRcvDisconnect( sock->channel, NULL );
	}
	
	// Do we need to ?
	// (masahiro minami<elsur@aaa.letter.co.jp>)
	//YieldToAnyThread();
}

/* Create a new TCPsocket */
// Because TCPsocket structure gets bigger and bigger,
// I think we'd better have a constructor function and delete function.
// ( 01/02/25 masahiro minami<elsur@aaa.letter.co.jp> )
static TCPsocket AsyncTCPNewSocket()
{
	TCPsocket sock;
	
	sock = (TCPsocket)malloc(sizeof(*sock));
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
	sock->readShutdown = sock->writeShutdown = sock->connected = false;
	sock->error = 0;
	sock->config = NULL;
	sock->nextListener = NULL;
	sock->sflag = 0;
	return sock;	
}

// hmmm.... do we need this ???
// ( 01/02/25 masahiro minami<elsur@aaa.letter.co.jp>)
static void AsycnTCPDeleteSocket( TCPsocket sock )
{
	SDLNet_TCP_Close( sock );
}
/* Open a TCP network socket
   If 'remote' is NULL, this creates a local server socket on the given port,
   otherwise a TCP connection to the remote host and port is attempted.
   The newly created socket is returned, or NULL if there was an error.

   ( re-written by masahiro minami<elsur@aaa.letter.co.jp>
     Now endpoint is created in Async mode.
     01/02/20 )
*/
TCPsocket SDLNet_TCP_Open(IPaddress *ip)
{
	EndpointRef dummy = NULL;

	TCPsocket sock = AsyncTCPNewSocket();
	if( ! sock)
		return NULL;

	// Determin whether bind locally, or connect to remote
	if ( (ip->host != INADDR_NONE) && (ip->host != INADDR_ANY) )
	{
		// ######## Connect to remote
		OTResult stat;
		InetAddress inAddr;
		TBind bindReq;

		// Open endpoint
		sock->error = OTAsyncOpenEndpoint(
			OTCreateConfiguration(kTCPName), NULL, &(sock->info),
			(OTNotifyProcPtr)(AsyncTCPNotifier),
			sock );

		AsyncTCPPopEvent( sock );
		while( !sock->error && !( sock->completion & CompleteMask(T_OPENCOMPLETE)))
		{
			//SetThreadState( kCurrentThreadID, kReadyThreadState, kNoThreadID );
			//YieldToAnyThread();
			//WaitNextEvent(everyEvent, &macEvent, 1, NULL);
			AsyncTCPPopEvent( sock );
		}

		if( !sock->channel )
		{
			SDLNet_SetError("OTAsyncOpenEndpoint failed --- client socket could not be opened");
			goto error_return;
		}

		// Set blocking mode
		// I'm not sure if this is a good solution....
		// Check out Apple's sample code, OT Virtual Server
		// ( 010314 masahiro minami<elsur@aaa.letter.co.jp>)

		sock->error = OTSetBlocking( sock->channel );
		if( sock->error != kOTNoError )
		{
			SDLNet_SetError("OTSetBlocking() returned an error");
			goto error_return;
		}

		// Bind the socket
		OTInitInetAddress(&inAddr, 0, 0 );
		bindReq.addr.len = sizeof( InetAddress );
		bindReq.addr.buf = (unsigned char*)&inAddr;
		bindReq.qlen = 0;

		sock->error = OTBind( sock->channel, &bindReq, NULL );
		AsyncTCPPopEvent(sock);
		while( !sock->error && !( sock->completion & CompleteMask(T_BINDCOMPLETE)))
		{
			//YieldToAnyThread();
			//WaitNextEvent(everyEvent, &macEvent, 1, NULL);
			AsyncTCPPopEvent(sock);
		}


		switch( stat = OTGetEndpointState( sock->channel ))
		{
			InetAddress inAddr;
			TCall sndCall;
			OTResult res;

			case T_OUTCON:
				SDLNet_SetError("SDLNet_Open() failed -- T_OUTCON");
				goto error_return;
				break;
			case T_IDLE:
				sock->readShutdown = false;
				sock->writeShutdown = false;
				sock->event &=~T_CONNECT;

				OTMemzero(&sndCall, sizeof(TCall));
				OTInitInetAddress(&inAddr, ip->port, ip->host );
				sndCall.addr.len = sizeof(InetAddress);
				sndCall.addr.buf = (unsigned char*)&inAddr;
				sock->connected = 0;
				res = OTConnect( sock->channel, &sndCall, NULL );
				AsyncTCPPopEvent(sock);
				while( sock->error == kOTNoDataErr || !sock->connected )
					AsyncTCPPopEvent(sock);
				break;
			default:
				// What's to be done ? (TODO)
				SDLNet_SetError("SDLNet_TCP_Open() failed -- EndpointState not good");
				goto error_return;

		}
		if( !(sock->event & (T_CONNECT|T_DISCONNECT)))
			goto error_return;

		AsyncTCPPopEvent( sock );
		while( !(sock->event & (T_CONNECT|T_DISCONNECT)))
		{
			AsyncTCPPopEvent( sock );
		}
		// OTConnect successfull
		if( sock->event & T_CONNECT)
		{
			sock->remoteAddress.host = inAddr.fHost;
			sock->remoteAddress.port = inAddr.fPort;
			sock->sflag = false;
		}
		else
		{
			// OTConnect failed
			sock->event &= ~T_DISCONNECT;
			goto error_return;
		}
	}
	else
	{
		// ######## Bind locally
		TBind bindReq;
		InetAddress	inAddr;

	// First, get InetInterfaceInfo.
	// I don't search for all of them.
	// Does that matter ?

		sock->error = OTAsyncOpenEndpoint(
			OTCreateConfiguration("tilisten, tcp"), NULL, &(sock->info),
			(OTNotifyProcPtr)(AsyncTCPNotifier),
			sock);
		AsyncTCPPopEvent( sock );
		while( !sock->error && !( sock->completion & CompleteMask( T_OPENCOMPLETE)))
		{
			AsyncTCPPopEvent( sock );
		}

		if( ! sock->channel )
		{
			SDLNet_SetError("OTAsyncOpenEndpoint failed --- server socket could not be opened");
			goto error_return;
		}

		// Create a master OTConfiguration
		sock->config = OTCreateConfiguration(kTCPName);
		if( ! sock->config )
		{
			SDLNet_SetError("Could not create master OTConfiguration");
			goto error_return;
		}

		// Bind the socket
		OTInitInetAddress(&inAddr, ip->port, 0 );
		inAddr.fAddressType = AF_INET;
		bindReq.addr.len = sizeof( InetAddress );
		bindReq.addr.buf = (unsigned char*)&inAddr;
		bindReq.qlen = 35;	// This number is NOT well considered. (TODO)
		sock->localAddress.host = inAddr.fHost;
		sock->localAddress.port = inAddr.fPort;
		sock->sflag = true;
		
		sock->error = OTBind( sock->channel, &bindReq, NULL );
		AsyncTCPPopEvent(sock);
		while( !sock->error && !( sock->completion & CompleteMask(T_BINDCOMPLETE)))
		{
			AsyncTCPPopEvent(sock);
		}
		if( sock->error != kOTNoError )
		{
			SDLNet_SetError("Could not bind server socket");
			goto error_return;
		}
		
		if( dummy )
			OTCloseProvider( dummy );

	}
	
	sock->ready = 0;
	return sock;
	
	error_return:
	if( dummy )
		OTCloseProvider( dummy );
	SDLNet_TCP_Close( sock );
	return NULL;	
}

/* Accept an incoming connection on the given server socket.
   The newly created socket is returned, or NULL if there was an error.
*/
TCPsocket SDLNet_TCP_Accept(TCPsocket server)
{
	
	/* Only server sockets can accept */
	if ( ! server->sflag ) {
		SDLNet_SetError("Only server sockets can accept()");
		return(NULL);
	}
	server->ready = 0;

	/* Accept a new TCP connection on a server socket */
	{
		InetAddress peer;
		TCall peerinfo;
		TCPsocket sock = NULL;
		Boolean mustListen = false;
		OTResult err;
		
		memset(&peerinfo, 0, (sizeof peerinfo ));
		peerinfo.addr.buf = (Uint8 *) &peer;
		peerinfo.addr.maxlen = sizeof(peer);
		
		while( mustListen || !sock )
		{
			// OTListen
			// We do NOT block ---- right thing ? (TODO)
			err = OTListen( server->channel, &peerinfo );

			if( err )
				goto error_return;
			else
			{
				mustListen = false;
				sock = AsyncTCPNewSocket();
				if( ! sock )
					goto error_return;
			}
		}
		if( sock )
		{
			// OTAsyncOpenEndpoint
			server->error = OTAsyncOpenEndpoint( OTCloneConfiguration( server->config ),
				NULL, &(sock->info), (OTNotifyProcPtr)AsyncTCPNotifier, sock );
			AsyncTCPPopEvent( sock );
			while( !sock->error && !( sock->completion & CompleteMask( T_OPENCOMPLETE)))
			{
				AsyncTCPPopEvent( sock );
			}
			if( ! sock->channel )
			{
				mustListen = false;
				goto error_return;
			}
			
			// OTAccept
			server->completion &= ~(CompleteMask(T_ACCEPTCOMPLETE));
			server->error = OTAccept( server->channel, sock->channel, &peerinfo );
			AsyncTCPPopEvent( server );
			while( !(server->completion & CompleteMask(T_ACCEPTCOMPLETE)))
			{
				AsyncTCPPopEvent( server );
			}
			
			switch( server->error )
			{
				case kOTLookErr:
					switch( OTLook(server->channel ))
					{
						case T_LISTEN:
							mustListen = true;
							break;
						case T_DISCONNECT:
							goto error_return;
					}
					break;
				case 0:
					sock->nextListener = server->nextListener;
					server->nextListener = sock;
					sock->remoteAddress.host = peer.fHost;
					sock->remoteAddress.port = peer.fPort;
					return sock;
					// accept successful
					break;
				default:
					free( sock );
			}
		}
		sock->remoteAddress.host = peer.fHost;
		sock->remoteAddress.port = peer.fPort;
		sock->sflag = 0;
		sock->ready = 0;

		/* The socket is ready */
		return(sock);
	
	// Error; close the socket and return	
	error_return:
		SDLNet_TCP_Close(sock);
		return(NULL);
	}
}

/* Get the IP address of the remote system associated with the socket.
   If the socket is a server socket, this function returns NULL.
*/
IPaddress *SDLNet_TCP_GetPeerAddress(TCPsocket sock)
{
	if ( sock->sflag ) {
		return(NULL);
	}
	return(&sock->remoteAddress);
}

/* Send 'len' bytes of 'data' over the non-server socket 'sock'
   This function returns the actual amount of data sent.  If the return value
   is less than the amount of data sent, then either the remote connection was
   closed, or an unknown socket error occurred.
*/
int SDLNet_TCP_Send(TCPsocket sock, const void *datap, int len)
{
	const Uint8 *data = (const Uint8 *)datap;	/* For pointer arithmetic */
	int sent, left;

	/* Server sockets are for accepting connections only */
	if ( sock->sflag ) {
		SDLNet_SetError("Server sockets cannot send");
		return(-1);
	}

	/* Keep sending data until it's sent or an error occurs */
	left = len;
	sent = 0;
	errno = 0;
	do {
		len = OTSnd(sock->channel, (void *)data, left, 0);
		if (len == kOTFlowErr)
			len = 0;
		if ( len > 0 ) {
			sent += len;
			left -= len;
			data += len;
		}
		// Do we need to ?
		// ( masahiro minami<elsur@aaa.letter.co.jp> )
		// (TODO)
		//WaitNextEvent(everyEvent, &macEvent, 1, NULL);
		//AsyncTCPPopEvent(sock);
	} while ( (left > 0) && (len > 0) );

	return(sent);
}

/* Receive up to 'maxlen' bytes of data over the non-server socket 'sock',
   and store them in the buffer pointed to by 'data'.
   This function returns the actual amount of data received.  If the return
   value is less than or equal to zero, then either the remote connection was
   closed, or an unknown socket error occurred.
*/
int SDLNet_TCP_Recv(TCPsocket sock, void *data, int maxlen)
{
	int len = 0;
	OSStatus res;
	/* Server sockets are for accepting connections only */
	if ( sock->sflag ) {
		SDLNet_SetError("Server sockets cannot receive");
		return(-1);
	}

	do
	{
		res = OTRcv(sock->channel, data, maxlen-len, 0);
		if (res > 0) {
			len = res;
		}

#ifdef DEBUG_NET
		if ( res != kOTNoDataErr )
			printf("SDLNet_TCP_Recv received ; %d\n", res );
#endif
		
		AsyncTCPPopEvent(sock);
		if( res == kOTLookErr )
		{
			res = OTLook(sock->channel );
			continue;
		}
	} while ( (len == 0) && (res == kOTNoDataErr) );

	sock->ready = 0;
	if ( len == 0 ) { /* Open Transport error */
#ifdef DEBUG_NET
		printf("Open Transport error: %d\n", res);
#endif
		return(-1);
	}
	return(len);
}

/* Close a TCP network socket */
void SDLNet_TCP_Close(TCPsocket sock)
{
	if ( sock != NULL ) {
		if ( sock->channel != INVALID_SOCKET ) {
			//closesocket(sock->channel);
			OTSndOrderlyDisconnect( sock->channel );
		}
		free(sock);
	}
}

#else /* !MACOS_OPENTRANSPORT */

struct _TCPsocket {
	int ready;
	SOCKET channel;
	IPaddress remoteAddress;
	IPaddress localAddress;
	int sflag;
};

/* Open a TCP network socket
   If 'remote' is NULL, this creates a local server socket on the given port,
   otherwise a TCP connection to the remote host and port is attempted.
   The newly created socket is returned, or NULL if there was an error.
*/
TCPsocket SDLNet_TCP_Open(IPaddress *ip)
{
	TCPsocket sock;
	struct sockaddr_in sock_addr;

	/* Allocate a TCP socket structure */
	sock = (TCPsocket)malloc(sizeof(*sock));
	if ( sock == NULL ) {
		SDLNet_SetError("Out of memory");
		goto error_return;
	}

	/* Open the socket */
	sock->channel = socket(AF_INET, SOCK_STREAM, 0);
	if ( sock->channel == INVALID_SOCKET ) {
		SDLNet_SetError("Couldn't create socket");
		goto error_return;
	}

	/* Connect to remote, or bind locally, as appropriate */
	if ( (ip->host != INADDR_NONE) && (ip->host != INADDR_ANY) ) {

	// #########  Connecting to remote
	
		memset(&sock_addr, 0, sizeof(sock_addr));
		sock_addr.sin_family = AF_INET;
		sock_addr.sin_addr.s_addr = ip->host;
		sock_addr.sin_port = ip->port;

		/* Connect to the remote host */
		if ( connect(sock->channel, (struct sockaddr *)&sock_addr,
				sizeof(sock_addr)) == SOCKET_ERROR ) {
			SDLNet_SetError("Couldn't connect to remote host");
			goto error_return;
		}
		sock->sflag = 0;
	} else {

	// ##########  Binding locally

		memset(&sock_addr, 0, sizeof(sock_addr));
		sock_addr.sin_family = AF_INET;
		sock_addr.sin_addr.s_addr = INADDR_ANY;
		sock_addr.sin_port = ip->port;

/*
 * Windows gets bad mojo with SO_REUSEADDR:
 * http://www.devolution.com/pipermail/sdl/2005-September/070491.html
 *   --ryan.
 */
#ifndef WIN32
		/* allow local address reuse */
		{ int yes = 1;
			setsockopt(sock->channel, SOL_SOCKET, SO_REUSEADDR, (char*)&yes, sizeof(yes));
		}
#endif

		/* Bind the socket for listening */
		if ( bind(sock->channel, (struct sockaddr *)&sock_addr,
				sizeof(sock_addr)) == SOCKET_ERROR ) {
			SDLNet_SetError("Couldn't bind to local port");
			goto error_return;
		}
		if ( listen(sock->channel, 5) == SOCKET_ERROR ) {
			SDLNet_SetError("Couldn't listen to local port");
			goto error_return;
		}

		/* Set the socket to non-blocking mode for accept() */
#if defined(__BEOS__) && defined(SO_NONBLOCK)
		/* On BeOS r5 there is O_NONBLOCK but it's for files only */
		{
			long b = 1;
			setsockopt(sock->channel, SOL_SOCKET, SO_NONBLOCK, &b, sizeof(b));
		}
#elif defined(O_NONBLOCK)
		{
			fcntl(sock->channel, F_SETFL, O_NONBLOCK);
		}
#elif defined(WIN32)
		{
			unsigned long mode = 1;
			ioctlsocket (sock->channel, FIONBIO, &mode);
		}
#elif defined(__OS2__)
		{
			int dontblock = 1;
			ioctl(sock->channel, FIONBIO, &dontblock);
		}
#else
#warning How do we set non-blocking mode on other operating systems?
#endif
		sock->sflag = 1;
	}
	sock->ready = 0;

#ifdef TCP_NODELAY
	/* Set the nodelay TCP option for real-time games */
	{ int yes = 1;
	setsockopt(sock->channel, IPPROTO_TCP, TCP_NODELAY, (char*)&yes, sizeof(yes));
	}
#endif /* TCP_NODELAY */

	/* Fill in the channel host address */
	sock->remoteAddress.host = sock_addr.sin_addr.s_addr;
	sock->remoteAddress.port = sock_addr.sin_port;

	/* The socket is ready */
	return(sock);

error_return:
	SDLNet_TCP_Close(sock);
	return(NULL);
}

/* Accept an incoming connection on the given server socket.
   The newly created socket is returned, or NULL if there was an error.
*/
TCPsocket SDLNet_TCP_Accept(TCPsocket server)
{
	TCPsocket sock;
	struct sockaddr_in sock_addr;
	int sock_alen;

	/* Only server sockets can accept */
	if ( ! server->sflag ) {
		SDLNet_SetError("Only server sockets can accept()");
		return(NULL);
	}
	server->ready = 0;

	/* Allocate a TCP socket structure */
	sock = (TCPsocket)malloc(sizeof(*sock));
	if ( sock == NULL ) {
		SDLNet_SetError("Out of memory");
		goto error_return;
	}

	/* Accept a new TCP connection on a server socket */
	sock_alen = sizeof(sock_addr);
	sock->channel = accept(server->channel, (struct sockaddr *)&sock_addr,
#ifdef USE_GUSI_SOCKETS
						(unsigned int *)&sock_alen);
#else
								&sock_alen);
#endif
	if ( sock->channel == SOCKET_ERROR ) {
		SDLNet_SetError("accept() failed");
		goto error_return;
	}
#ifdef WIN32
	{
		/* passing a zero value, socket mode set to block on */
		unsigned long mode = 0;
		ioctlsocket (sock->channel, FIONBIO, &mode);
	}
#elif defined(O_NONBLOCK)
	{
		int flags = fcntl(sock->channel, F_GETFL, 0);
		fcntl(sock->channel, F_SETFL, flags & ~O_NONBLOCK);
	}
#endif /* WIN32 */
	sock->remoteAddress.host = sock_addr.sin_addr.s_addr;
	sock->remoteAddress.port = sock_addr.sin_port;

	sock->sflag = 0;
	sock->ready = 0;

	/* The socket is ready */
	return(sock);

error_return:
	SDLNet_TCP_Close(sock);
	return(NULL);
}

/* Get the IP address of the remote system associated with the socket.
   If the socket is a server socket, this function returns NULL.
*/
IPaddress *SDLNet_TCP_GetPeerAddress(TCPsocket sock)
{
	if ( sock->sflag ) {
		return(NULL);
	}
	return(&sock->remoteAddress);
}

/* Send 'len' bytes of 'data' over the non-server socket 'sock'
   This function returns the actual amount of data sent.  If the return value
   is less than the amount of data sent, then either the remote connection was
   closed, or an unknown socket error occurred.
*/
int SDLNet_TCP_Send(TCPsocket sock, const void *datap, int len)
{
	const Uint8 *data = (const Uint8 *)datap;	/* For pointer arithmetic */
	int sent, left;

	/* Server sockets are for accepting connections only */
	if ( sock->sflag ) {
		SDLNet_SetError("Server sockets cannot send");
		return(-1);
	}

	/* Keep sending data until it's sent or an error occurs */
	left = len;
	sent = 0;
	errno = 0;
	do {
		len = send(sock->channel, (const char *) data, left, 0);
		if ( len > 0 ) {
			sent += len;
			left -= len;
			data += len;
		}
	} while ( (left > 0) && ((len > 0) || (errno == EINTR)) );

	return(sent);
}

/* Receive up to 'maxlen' bytes of data over the non-server socket 'sock',
   and store them in the buffer pointed to by 'data'.
   This function returns the actual amount of data received.  If the return
   value is less than or equal to zero, then either the remote connection was
   closed, or an unknown socket error occurred.
*/
int SDLNet_TCP_Recv(TCPsocket sock, void *data, int maxlen)
{
	int len;

	/* Server sockets are for accepting connections only */
	if ( sock->sflag ) {
		SDLNet_SetError("Server sockets cannot receive");
		return(-1);
	}

	errno = 0;
	do {
		len = recv(sock->channel, (char *) data, maxlen, 0);
	} while ( errno == EINTR );

	sock->ready = 0;
	return(len);
}

/* Close a TCP network socket */
void SDLNet_TCP_Close(TCPsocket sock)
{
	if ( sock != NULL ) {
		if ( sock->channel != INVALID_SOCKET ) {
			closesocket(sock->channel);
		}
		free(sock);
	}
}

#endif /* MACOS_OPENTRANSPORT */
