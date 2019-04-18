"""IRC Application
Submitted by : Harini G T

References used: http://www.bogotobogo.com/python/python_network_programming_tcp_server_client_chat_server_chat_client_select.php
https://pythonspot.com/python-network-sockets-programming-tutorial/
"""
import select,socket,sys
READ_BUFFER = 1000
QUIT_STRING ="[quit]"
MAX_CLIENTS = 10
HOST = ''
SOCKET_LIST = []
RECV_BUFFER = 4096
PORT = 9009


choice =b'***************************IRC-BOT***************************************\n\n' \
       + b'*************************************************************************\n\n' \
       + b'**[Enter] room_name -- to create a room or join an existing room       **\n\n' \
       + b'**[Message] room_name  -- to send messages to a specific room          **\n\n' \
       + b'**[List Rooms] -- to list all rooms                                    **\n\n' \
       + b'**[List Clients] -- to list all the clients in the application         **\n\n' \
       + b'**[Private] member_name -- for a private chat                          **\n\n' \
       + b'**[Exit] -- to leave room                                              **\n\n' \
       + b'**[Quit] --  to quit the application                                   **\n\n' \
       + b'**[Transfer File] member_name -- to transfer a file to a client        **\n\n' \
       + b'**[Help] -- to view the options                                        **\n\n' \
       + b'**Note : All the commands have the pattern ["command"]                 **\n\n' \
       + b'*************************************************************************\n\n' \



def chat_server():
    ''' This method invokes the server . It binds the client and server and adds the coonection to
    list of connections in the server.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind((HOST,PORT))
    s.listen(MAX_CLIENTS)
    IRC_CHAT = IRC_CHAT_APP()
    connection_list = []
    connection_list.append(s)
    print("Chat server started on port " + str(PORT))
    while True:
        ready_to_read, ready_to_write, in_error_sockets = select.select(connection_list, [], [])
        for MEMBER in ready_to_read:
            if MEMBER is s:
                sockfd, add = MEMBER.accept()
                new_client = IRC_CLIENT(sockfd)
                connection_list.append(new_client)
                new_client.socket.sendall(b'Please enter your name:\n')
            else:
                msg = MEMBER.socket.recv(READ_BUFFER)
                if not msg:
                    IRC_CHAT.remove_client_chat_room(MEMBER)
                if msg:
                    msg = msg.decode().lower()
                    IRC_CHAT.data_controller(MEMBER, msg)
                else:
                    MEMBER.socket.close()
                    connection_list.remove(MEMBER)
        for sock in in_error_sockets:
            sock.close()
            connection_list.remove(sock)

class IRC_CHAT_APP:
    '''This class represents the IRC chat application. It stores the details of all the rooms
    in the application and all required client and room mappings'''
    def __init__(self):
        self.rooms = {}
        self.room_member_map = {}
        self.members_map = {}
        self.msg_dict = {'no_room':'There are no active chatrooms at the moment\n'
                                  + 'usage:[enter] room_name to create a room.\n' ,
                         'name_error' :'"\nThe username cannot start with "["\n Please choose a '
                                       'valid name\n"' +b'Please enter your name:\n',
                         'not_entered': 'Please enter a room  \n' \
                       + 'Use [list rooms] to see available rooms! \n' \
                       + 'Use [[enter] room_name] to join a room! \n' ,
                         'invalid_name' : '"\nThe username cannot start with the '
                                          'character[\n Please choose a valid name\n"' + b'Please enter your name:\n',
                         'name_exists' : '\n Username already exists\n' + b'Please enter your name:\n' ,
                         'enter_room_error' : '\nUsage : [Enter] room_name\n\nPlease use [Help] to see all the options\n',
                         'room_error' : '\nThe room name should start with the word "Room"\n ',
                         'message_room_error' : '\nUsage : [Message] room_name\n\nPlease use [Help] to see all the options\n',
                         'list_room' :'Please use [list rooms] to list all the rooms and clients\n',
                         'not_in_room' : 'You are not part of the room\n'
}

    def start_window(self,client):
        '''This method is used to display all the options available in the IRC application'''
        return self.send_data(client,choice)

    def send_data(self,client,out):
        ''' :param client: The client to add to the application
            :param data: The incoming message from the client
            This is a utility method to send messages/data to the the client'''
        client.socket.sendall(out)

    def get_member_name(self, client, msg):
        ''' :param client: The client to add to the application
            :param data: The incoming message from the client
        This methods fetches the name of the client and checks for the validity
        of the name before the client is added to the application'''
        name = msg.split()[1]
        if str(name).startswith('['):
            out = self.msg_dict['invalid_name']
            self.send_data(client, out.encode())
        elif str(name) in self.members_map:
            out = self.msg_dict['name_exists']
            self.send_data(client,out.encode())
        else:
            client.name = name
            print("New connection from:  ", client.name)
            self.members_map[client.name] = client
            out = " Welcome ," + client.name + "\n\n Choose from the options below\n\n"
            self.send_data(client,out.encode())
            self.start_window(client)

    def check_room_validity(self,client,data):
        '''  :param client: The client to add to the application
             :param data: The incoming message from the client
         This method implements the the checks for all the errors when the clients enters
         commands to enter a room or message a room or private chat'''
        if len(data.split()) < 2:
            out = self.msg_dict['enter_room_error']
            self.send_data(client, out.encode())
        else:
            room_name = data.split()[1]
            if not str(room_name).startswith("room"):
                out = self.msg_dict['room_error']
                self.send_data(client, out.encode())

    def message_specific_room(self,client,data):
        ''' :param client: The client to add to the application
            :param data: The incoming message from the client
            This method implements the functionality send messages to a specific room '''
        if len(data.split()) < 3:
            out = self.msg_dict['message_room_error']
            self.send_data(client, out.encode())
        elif not str(data.split()[1]).startswith("room"):
            out = self.msg_dict['room_error']
            self.send_data(client, out.encode())
        elif client.name + "-" + str(data.split()[1]) not in self.room_member_map:
            out = self.msg_dict['not_entered']+ str(data.split()[1]) + self.msg_dict['list_room']
            self.send_data(client,out.encode())
        else:
            data_to_send = data.split()
            message_room = str(data.split()[1])
            print("Message to specific room from ", client.name, " to room ", message_room)
            del data_to_send[0]
            del data_to_send[1]
            self.rooms[self.room_member_map[client.name + "-" + message_room]].broadcast(client,str(data_to_send).encode())

    def add_member_to_room(self, client, data):
        ''' :param client: The client to add to the application
            :param data: The incoming message from the client
            This method is used to add the client to the application.'''
        same_room = False
        if len(data.split()) < 2:
            out = "\nUsage : [Enter] room_name\n\nPlease use [Help] to see all the options\n"
            self.send_data(client, out)
        elif not str(data.split()[1]).startswith("room"):
            out = "\nThe room name should start with the word 'Room'\n "
            self.send_data(client, out)
        else:
            room_name = data.split()[1]
            client.active_room = room_name
            if client.name + "-" + room_name in self.room_member_map and \
                    self.room_member_map[client.name + "-" + room_name] == room_name:
                out = b'You are already in room: ' + room_name.encode()
                self.send_data(client,out)
                same_room = True
            if not same_room:
                if not room_name in self.rooms:  # new room:
                    new_room = Room(room_name)
                    self.rooms[room_name] = new_room
                self.rooms[room_name].members.append(client)
                self.rooms[room_name].welcome_new(client)
                self.room_member_map[client.name + "-" + room_name] = room_name
                client.room_occupied.append(room_name)

    def exit_chatroom(self, client, data):
        ''' :param client: The client to add to the application
            :param data: The incoming message from the client
            This method implements the functionality to exit from a chat room '''
        roomname = ""
        for val in client.room_occupied:
            roomname = roomname + " , " + str(val)
        if len(data.split()) < 2:
            out = "\nUsage:[Exit] room_name\n"+"You are currently in " +roomname+"\nPlease use [Help] to see all the options\n"
            self.send_data(client,out)
        else:
            if len(data.split()) >= 2:  # error check
                room_to_exit = data.split()[1]
                if client.name + "-" + room_to_exit in self.room_member_map:
                    del self.room_member_map[client.name + "-" + client.active_room]
                    self.rooms[room_to_exit].remove_member(client)
                    print("Chat Client : " + client.name + "  has left" + room_to_exit + "\n")
                    client.socket.sendall("Thank you , " + client.name + "!! Have a nice day\n")
                    if len(self.rooms[room_to_exit].members) == 0:
                        del self.rooms[room_to_exit]
                else:
                    out = "\nPlease check the room name\n You are currently chatting is rooms " + roomname + "\n"
                    self.send_data(client,out.encode())
            else:
                self.start_window(client)


    def private_room(self,client,data):
        ''' :param client: The client to add to the application
            :param data: The incoming message from the client
            This method implements the functionality of private chat between two clients '''
        if len(data.split()) < 2:
            out = "\nUsage :[Private] client_name\n\nPlease use [Help] to see all the options\n"
            self.send_data(client, out)
        elif str(data.split()[1])==client.name:
            out = "\nPlease enter a client name\n\nPlease use [Help] to see all the options\n"
            self.send_data(client, out)
        elif str(data.split()[1]) not in self.members_map:
            out = "\nThe Client :" + str(data.split()[1]) + "doesn't exist.\nPlease use [List Clients] to view all the clients online\n"
            self.send_data(client, out)
        else:
            out = "Entering private chat with :" + str(data.split()[1]) + "\n"
            out1 = "Private chat from :" + client.name
            private_client_name = data.split()[1]
            self.send_data(private_client_name,out1.encode())
            self.send_data(client,out.encode())
            new_client = self.members_map[private_client_name]
            personal_room = Room("private-" + client.name + "-" + private_client_name)
            self.rooms["private-" + client.name + "-" + private_client_name] = personal_room
            self.rooms["private-" + client.name + "-" + private_client_name].members.append(client)
            self.rooms["private-" + client.name + "-" + private_client_name].members.append(new_client)
            self.room_member_map[client.name + "-" + "private-" + client.name + "-" + private_client_name] = "personal-" + client.name + "-" + private_client_name
            self.room_member_map[private_client_name + "-" + "private-" + client.name + "-" + private_client_name] = "personal-" + client.name + "-" + private_client_name
            client.active_room = "private-" + client.name + "-" + private_client_name
            client.name + "-" + private_client_name
            new_client.active_room = "private-" + client.name + "-" + private_client_name

    def quit_application(self, client):
        ''' :param client: The client to add to the application
            This method implements the functionality to quit the IRC CHAT Application '''
        client.socket.sendall(QUIT_STRING.encode())
        self.remove_client_chat_room(client)

    def list_clients(self, client):
        ''' :param client: The client to add to the application
            This method implements the functionality to list all the clients in the application'''
        out = " "
        for val in self.members_map:
            out+= "\n " + val
        out += "\n"
        self.send_data(client, out)

    def list_rooms(self, client):
        ''' :param client: The client to add to the application
        This method implements the functionality to list all the rooms along with its clients in the application'''
        if len(self.rooms) == 0:
            out = self.msg_dict['no_room']
            self.send_data(client,out.encode())
        else:
            out = 'List of all the rooms and clients in the application'
            for room in self.rooms:
                if 'private' not in room:
                    print(self.rooms[room].members)
                    out += '\n['+room + "-->" + str(len(self.rooms[room].members)) + " member(s) ]\n"
                    for member1 in self.rooms[room].members:
                        out += member1.name + " "
            out +="\n\n"
            self.send_data(client,out.encode())
                
   def remove_client_chat_room(self, client):
    ''' :param client: The client to add to the application
        :param data: The incoming message from the client
        This method implements the functionality remove a client from the chat room '''
            if client.name + "-" + client.active_room in self.room_member_map:
            self.rooms[self.room_member_map[client.name + "-" + client.active_room]].remove_member(client)
            del self.room_member_map[client.name + "-" + client.active_room]
            print("Member  : " + client.name + " is offline\n")


    def data_controller(self, client, data):
        ''' :param client: The client to add to the application
            :param data: The incoming message from the client
        This method is the controller of the applcations. This is interface between the commands and
        the respective definitions'''
        print(client.name + " says: " + data)
        if "name:" in data:
            self.get_member_name(client, data)
        elif "[enter]" in data:
            self.add_member_to_room(client, data)
        elif "[list rooms]" in data:
            self.list_rooms(client)
        elif "[list clients]" in data:
            self.list_clients(client)
        elif "[help]" in data:
            self.start_window(client)
        elif "[exit]" in data:
            self.exit_chatroom(client, data)
        elif "[quit]" in data:
            self.quit_application(client)
        elif "[private]" in data:
            self.private_room(client,data)
        elif "[message]" in data:
            print("detected message")
            self.message_specific_room(client,data)
        elif client.name + "-" + client.active_room in self.room_member_map and (len(self.members_map) <2):
            out = "\nThere are no clients in the room. Please wait till a new member joins or join other available rooms.\n "
            self.send_data(client,out)
        elif not data:
            self.remove_member(client)
        else:
            if client.name + "-" + client.active_room in self.room_member_map:
                self.rooms[self.room_member_map[client.name + "-" + client.active_room]].broadcast(client,data.encode())
            else:
                out = self.msg_dict['not_in_room']
                self.send_data(client,out.encode())



class Room:
    ''' This class represents a chat room in the IRC application.
    It stores all the details of a chat room and the members in the room'''
    def __init__(self, name):
        self.members = []  # a list of sockets
        self.name = name

    def welcome_new(self, from_member):
        ''' :param from from_member: The client that was newly added to the application
            This is a utility method to welcome a new member to the IRC application '''
        msg = self.name + " welcomes: " + from_member.name + '\n'
        for member in self.members:
            member.socket.sendall(msg.encode())

    def broadcast(self, from_member, msg):
        ''' :param from_member: The client that wants to send the message
            :param msg: The incoming message from the client
        This method  broadcasts the message to a chat room'''
        msg = from_member.name.encode() + b":" + msg
        for member in self.members:
            member.socket.sendall(msg)

    def remove_member(self, member):
        ''' :param from_member: The client that wants to send the message
            :param msg: The incoming message from the client
            This method  is used to remove a client from the chat room'''
        self.members.remove(member)
        leave_msg = member.name.encode() + b"  has left the room\n"
        self.broadcast(member, leave_msg)


class IRC_CLIENT:
    """ This class represents a client in the IRC applcation"""
    def __init__(self, socket, name="new_client", active_room="new_room"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.room_occupied = []
        self.active_room = active_room

    def fileno(self):
        return self.socket.fileno()

if __name__ == '__main__':
    sys.exit(chat_server())
