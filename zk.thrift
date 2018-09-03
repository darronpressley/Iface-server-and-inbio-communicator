namespace java com.zktechnology.zkproto

// Exception causes (both sync and control server here)
enum ZKProtoErrorCause {
	// Common (0-50)
	SERVER_ERROR = 0,		// Generic server error
	BAD_VERSION = 1,		// Protocol version not supported
	NO_OPEN = 2,			// Client called pull/push without previous open
	BAD_COMMAND = 3,		// Unrecognized command or wrong data 
	ALREADY_OPEN = 4,		// Client has already called open()
	NOT_AUTHORIZED = 5,		// Client connection refused
	TIMEOUT = 6,			// Operation timed out
	WRONG_LOGIN = 7,		// Incorrect login/password
	
	// Sync server (50-99)
	CONFLICT = 50,			// DB conflict in server	
	WRONG_TIMESTAMP = 51,	// Client clock is not synchronized with server
	NOT_REPLICATED = 52,	// Client called push when not replicated	
	
	// Control server (100-149)
	ZONE_NOT_EMPTY = 100,	// Client tried to delete non-empty zone
	NOT_CONNECTED = 101,	// Client is not currently connected
}

// ZKProto exception definition 
exception ZKProtoException {
  	1: required ZKProtoErrorCause xcause,	// Cause of the exception
	2: optional i32 index,				// First index in the list that failed if any
	3: optional i64 opid,				// First operation ID that failed if any
	4: optional string data,			// Extra data about the error
}

// Filter type
enum ZKProtoSyncTableFilterType {
	WHITE_LIST = 0,
	BLACK_LIST = 1,
}

// Structure returned from open() call
struct ZKProtoSyncAckInfo {
	1: optional string encryptedKey,	// Encrypted key for secure communication
}

// Table filter definition
struct ZKProtoSyncTableFilter {
	1: required ZKProtoSyncTableFilterType filter, 	// Filter type
	2: required list<string> tableList,				// List table filter
}

// Synchronization information
struct ZKProtoSyncOpenInfo {
	1: required i32 protocolVersion,				// ZKProto version
	2: required i64 clientId,						// Client UUID
	3: required string customId,					// Customer ID
	4: optional i32 maxOperations,					// Max size of ZKProtoOperations (in bytes)
	5: optional string publicKey,					// Public key for encryption start
	6: required i64 timestamp,						// Current client UTC time
	7: optional ZKProtoSyncTableFilter tableFilter, // Table filters if any
}

// Action for operations
enum ZKProtoSyncAction {
	NOP = 0,			// Do nothing or pure data
	INSERT = 1,			// DB Insert
	UPDATE = 2,			// DB Update
	DELETE = 3,			// DB Delete
	PUSH =  4,			// Force client to call push() 
	ACKNOWLEDGE = 5,	// Confirm operations done
}

// Operation to be performed
struct ZKProtoSyncOperation {
	1: required i64 id,						// Operation UUID (-1 if no ID)
	2: required ZKProtoSyncAction action,	// Action performed in operation
	3: optional i64 timestamp,				// UTC time when this operation happened (can be null if no log required)
	4: optional binary data,				// Data for the action
	5: optional bool compressed,			// Flag if data is compressed
}

// Wrapper for a list of operations
struct ZKProtoSyncOperations {
	1: required list<ZKProtoSyncOperation> operations,	// List of operations	
	2: required bool last,								// Is this last part of a multipart?
}

// Server service interface (this is NOT an Android service, but a Thrift service)
// Answers are handled by exceptions, see the code
service ZKProtoSyncService {

	// Open communication
	// Returns true if device is already known, false otherwise (the device is new)
	ZKProtoSyncAckInfo open(1:ZKProtoSyncOpenInfo openInfo) throws (1:ZKProtoException e),
	
	// Synchronize data
	void push(1:list<ZKProtoSyncOperation> operations) throws (1:ZKProtoException e),
	
	// Pull operations to be performed
	ZKProtoSyncOperations pull() throws (1:ZKProtoException e),
}