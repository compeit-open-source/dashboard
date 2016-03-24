# COMPEIT Server REST API v2.0

For the second version of the COMPEIT Server REST API all URI begin with `/api/v2.0` 

## Authentication

All request are, for now, authenticated using HTTP-Basic authentication, thus all communication should preferably use SSL/TLS. In addition the API for manipulating objects also supports a method providing an API token. The authenticated user becomes the owner of the created objects and it the user is used for authorization with respects to queries and updates. All the APIs are JSON based both for the requests and the replies.

### User management

The basic user management is based around the `<user>` object and provides information about the registered users.

#### User object properties
The `<user>` has the following form:
```
{ 
	id: <int: the generated user id>
	email: <string: username
	name: <string: name>
}
```

#### User Methods

##### Query all users
```
GET: .../users
```
returns an array with all users
```
{ 
	users: [<user>, <user>, …]
}
```


##### Query a specific user
```
GET: .../users/<int:userId>
```
returns the specified user

The user is returned on the following form:
```
{ 
	user: <user>
}
```

### Circle management

Circles is used as the model for Authorization within the framework. The server provides methods for querying the circles for the user, its members and finding which circle a given other user is member of.

#### Circle properties

the <circle> object has the following properties:

```
{
    'id': <int: generated circle id>
    'name': <string: the name of the circle>,
    'members': [<member>, <member>, ...]
}
```

a <circle member> object has the following properties:

```
{
    'id': <int: generated id>,
    'email': <string: the email of the member>,
    'name': <string: the name of the member>
}
```

a <compact circle> object  
```
{
    'id': <int: circle id>,
    'name': <string: the name of the circle>
}
```


#### Circle Methods

##### Query circles
returns the circles defined by the user
```
GET: .../circles
```
returns an array with all circles
```
{ 
	circles: [<circle>, <circle>, …]
}
```

#### Query the members a specific circle 
returns the circle and the members of the specified circle
```
GET: .../circle/<int:circleId>
```
returns a specific circle and its members
```
{ 
	circle: <circle>
}
```

#### Query which circles a user is a member of 

returns the circles the specified user is a member of
```
GET: .../circle/user/<int:userId>
```
returns an array with all circles
```
{ 
	circles: [<compact circle>, <compact circle>, …]
}
```

### Object management

Objects are representations of tangible objects or IFTTT maker channel objects (Figure 15).

To provide support for integration with more generic REST-APIs, such as IFTTT Maker Channel, the Object Management API supports authentication via time limited tokens. To create a token valid for an object, a specific object method should be used, and `generate_token=True` and `token_lifetime=2678400` (seconds in a month) should be provided to generate a new token that is valid for a month. Then to use the token, it should be provided as an argument to the request as `token=eyJhbGc…`
IFTTT objects can either have inputs that will trigger a request to IFTTT when a value is set on the corresponding output, or for outputs that can be set by a `POST` from the IFTTT recipe.
When a value set triggers an IFTTT input, the resulting Maker Channel `POST` to IFTTT is populated with event from the `ifttt_maker_event` attribute from the Object. The body of the `POST` will be populated with `value1` as the current value for the input, `value2` as the name of the input and value3 as the name of the Object. If the `ifttt_maker_trigger_always` property is true then the each set (or `POST`) to the connected output will trigger a request to IFTTT, if not then only a change of the actual value will trigger a request.

#### Object properties

The `<object>` is returned on the following form:
```
{ 
	name: <string: Name of object>,
  	id: <string: unique identifier>,
  	description: <string: description>,
  	icon: <string: URL>,
  	type: <integer: object type (0 - Generic, 1 - IFTTT Maker)>,
  	ifttt_maker_key: <string: key>,
  	ifttt_maker_event: <string: event name>,
  	ifttt_maker_trigger_always: <boolean: always trigger ifttt post upon value post>,
  	user: <int: user identifier of creator>,
  	outputs: [<output>, <output>, ...],
  	inputs: [<input>, <input>, ...]
}
```

Where
```
<input> = {
    id: <int: unique id>
	name: <string: input name>,
	type: <string: An IO type>
}
```

and

```
<output> = {
    id: <int: unique id>
	name: <string: input name>,
	type: <string: An IO type>,
	value: <string: string representation of value>
}
```
#### Object Methods

##### Query all objects

```
GET: .../objects
```

returns a list with all objects, that the user can access, using the following form:

```
{ 
	objects: [<object>, <object>, ...]
}
```

##### Query a specific object

```
GET: .../objects/<string:objectId>
```
returns the objects with the specified id
```
{
	object: <object>
}
```

##### Query objects owned by a specific user

```
GET: .../objects/user/<int:userId>
```
returns an array with all objects that the user has to offer. 
```
{
	object: <object>
}
```

##### Create object
```
POST: .../objects
body: {
	name: <string: Name of object>,
	id: <string: A unique identifier>
	description: <string: A description>,
	icon: <string: URL>,
  	type: <integer: object type (0 - Generic, 1 - IFTTT Maker)>,
  	ifttt_maker_key: <string: key>,
  	ifttt_maker_event: <string: event name>,
  	ifttt_maker_trigger_always: <boolean: always trigger ifttt post upon value post>,
	outputs: [<output>, <output>, ...],
	inputs: [<input>, <input>, ...]
}
```

registers a new object. If the type is a IFTTT Maker Object then `ifttt_maker_key`, `ifttt_maker_event` and `ifttt_maker_trigger_always` is mandatory input values, if it is any other object then the properties are ignored.

##### Set an object output values
```
POST: .../objects/<string:objectId>/outputs/<string:name>
POST: .../outputs/<outputId>
```
```
body: {
	value: <value>
}
sets the value of output
```
##### Delete object
```
DELETE: .../objects/<string: object id>
```
deletes the specified object. 
All connections to its inputs, or outputs, will also be deleted. 

### Connection management

Connection management creates connections between Objects so that setting a value to an output (`POST`) triggers a change for the value of a connected input.

#### Connection properties
The `<connection>` has the following form:

```
{ 
	id: <int: connectionId>
	output: <int: from output id>
	from: <string: from object id>,
	out: <string: output name>
	input: <int: to input id>
	to: <string: to object id>,
	in: <string: input name>
}
```


#### Connection Methods

##### Creating a connection between objects
```
POST: .../connections
```

```
body : {
	from: <string: from object id>,
	out: <string: output name>,
	to: <string: to object id>,
	in: <string: input name>
}
```

connects the output of `output name` on `from object id` to `input name`  on `to object id` 


##### Retrieving connected objects
```
GET: .../connections
```
returns an array of all connections between objects
```
{
    		"connections": [ <connection>, <connection>, …]
}
```

```
GET: .../connections/<string: connectionId>
```
returns a connection between objects
```
{
    		"connection": <connection>
}
```

##### Delete connection
```
DELETE: .../connections/<string: connectionId>
```
deletes the specified connection 


### Room management

The Room objects represent the rooms in the system. The API provides methods for creating new rooms and querying for the rooms that the user can access. Each room has a specific type, which determines how the room looks and what you can do in the room.

#### Room properties

The `<room>` has the following properties:

```
{ 
    'id': <int: the generated room id>,
    'name': <string: the name of the room>,
    'type': <int: the room type>,
    'ownerId': <int: owner user id>
}
```

#### Room Methods

##### Create a new room
```
POST: .../room
body: {
	name: <string: Name of object>,
	type: <int: room type>
}
```

##### Query all accesible rooms
```
GET: .../rooms
```

returns a list with all rooms, that the user can access, using the following form:

```
{ 
	rooms: [<room>, <room>, ...]
}
```

##### Query a specific room
```
GET: .../rooms/<int:roomId>
```
returns the rooms with the specified id
```
{
	room: <room>
}
```

### JSON Object storage management

The platform provides support for storing generic JSON objects.

#### JSON Object properties

json_object
```
{
    'type': <string: the type of the JSON object>,
    'external_id': <string: the given external identifier (unique within type)>,
    'object': <string: the JSON object represented as a string>
}
```


#### JSON Object Methods

##### Create a JSON Object

```
POST: .../json_store/<string:type>/<string:external_id>
```
the saved JSON object is the body of the `POST` request

##### Query all JSON Objects available to the user

```
GET: .../json_store
```

returns a list with all json_objects, that the user can access, using the following form:

```
{
	json_objects: [<json_object>, <json_object>, ...]
}
```

##### Query all JSON Objects of a specified type available to the user

```
GET: .../json_store/<string:type>
```

returns a list of all json_objects, of the given type that the user can access, using the following form:

```
{
	json_objects: [<json_object>, <json_object>, ...]
}
```

##### Query a JSON Object available to the user

```
GET: .../json_store/<string:type>/<string:external_id>
```

returns the json_object with the specified id

```
{
	json_object: <json_object>
}
```

### File storage management

In addition, the platform provides support for uploading any type of binary files, such as images, documents, and so on. When uploading a file, a `file` object is created which contains the URL where the uploaded files can be accessed.

#### Uploaded file properties

The `file` object has the following properties: 

```
{
    'type': <string: the specified type>,
    'mime_type': <string: the mime type>,
    'filename': <string: the uploaded filename>,
    'url': <string: the URL where the file can be downloaded>
}
```

#### Uploaded file Methods

##### Query all uploaded files available to the user

```
GET: .../files
```
returns a list of  all files that the user can access, using the following form:

```
{
	files: [<file>, <file>, ...]
}
```

##### Query all uploaded files of a specific type available to the user

```
GET: .../files/<string:type>
```

returns a list of  all files, of the given type that the user can access, using the following form:

```
{
	files: [<file>, <file>, ...]
}
```

##### Query an uploaded files of a specific type and specific filename
```
GET: .../files/<string:type>/<string:filename>
```

returns the file with the specified type and filename


```
{
	file: <file>
}
```