
from sqlalchemy.orm import Session
from models.models import *
from sqlalchemy import and_
from services.db import engine

def get_all(user_id):
    with Session(engine) as session:
        rooms = session\
            .query(UserRoom.room_id, Room.room_name, Room.room_img, Room.room_type)\
            .join(Room, Room.room_id == UserRoom.room_id)\
            .filter(UserRoom.user_id == user_id)\
            .filter(UserRoom.is_deleted == False)\
            .all()
        
        rooms_1 = session\
            .query(UserRoom.room_id, UserRoom.user_id, User.fullname, User.avatar)\
            .join(Room, Room.room_id == UserRoom.room_id)\
            .join(User, User.user_id == UserRoom.user_id)\
            .filter(UserRoom.user_id != user_id)\
            .filter(UserRoom.is_deleted == False)\
            .all()

        room_map = {}
        for room in rooms_1:
            if room[0] not in room_map:
                room_map[room[0]] = {
                    "name": room[2],
                    "image": room[3],
                    "count": 1,
                }
            else:
                room_map[room[0]]["count"] += 1
        
        if not room_map:
            return []

        rooms_json = []
        for room in rooms:
            if room_map.get(room[0], {"count": 0})["count"] == 1 and room[3] == "single":
                room_exist = room_map[room[0]]
                rooms_json.append({
                    "id": room[0],
                    "name": room_exist["name"],
                    "image": room_exist["image"],
                })
            else:
                rooms_json.append({
                    "id": room[0],
                    "name": room[1],
                    "image": room[2],
                })

        return rooms_json

def get_by_id(room_id):
    with Session(engine) as session:
        room = session\
            .query(UserRoom.room_id, Room.room_master, Room.room_name, Room.room_img, Room.room_type, User.user_id, User.fullname, User.avatar, User.username, User.online, User.pb_key)\
            .join(Room, Room.room_id == UserRoom.room_id)\
            .join(User, User.user_id == UserRoom.user_id)\
            .filter(Room.room_id == room_id).all()
        
        if room is None or len(room) == 0:
            return None
        
        master = None
        if room[0][1] is not None:
            master = session\
                .query(User.user_id, User.fullname, User.username, User.avatar)\
                .filter(User.user_id == room[0][1])\
                .first()

        room_json = {
            "id": room[0][0],
            "name": room[0][2],
            "image": room[0][3],
            "type": room[0][4],
            "friends": []
        }     

        for ele in room:
            is_master = False
            if(master is not None and ele[5] == master[0]):
                is_master = True

            room_json["friends"].append({
                "user_id": ele[5],
                "fullname": ele[6],
                "avatar": ele[7],
                "username": ele[8],
                "online": ele[9],
                "is_master": is_master,
                "public_key": ele[10]
            })
        
        return room_json

def room_single_exist(user_id, friend_user_id):
    with Session(engine) as session:
        existing_room = session.query(Room.room_id)\
            .join(UserRoom, Room.room_id == UserRoom.room_id)\
            .filter(UserRoom.user_id.in_([user_id, friend_user_id]))\
            .filter(Room.room_type == "single")\
            .group_by(Room.room_id).\
            having(func.count(Room.room_id) == 2).\
            first()
        
        return existing_room        

def create(master, room_name, room_image, room_type="single"):
    with Session(engine) as session:
        room = Room(
            room_master=master,
            room_name=room_name,
            room_img=room_image,
            room_type=room_type
        )
        session.add(room)
        session.commit()
        return room.room_id
    
def join_users(room_id, users):
    with Session(engine) as session:
        for user_id in users:
            user_exit = session.query(UserRoom.user_id).filter(and_(UserRoom.room_id == room_id, UserRoom.user_id == user_id)).first()
            if user_exit is None:
                user_room = UserRoom(
                    user_id=user_id,
                    room_id=room_id
                )
                session.add(user_room)

        session.commit()

def leave_room(room_id, userId):
    with Session(engine) as session:
        user_room = session\
            .query(UserRoom)\
            .filter(UserRoom.room_id == room_id)\
            .filter(UserRoom.user_id == userId)\
            .first()
        
        if user_room is None:
            return None
        
        session.delete(user_room)
        session.commit()
        return user_room.id

def get_history(room_id):
    with Session(engine) as session:
        messages = session\
            .query(Message.message_id, Message.content, Message.author, User.avatar, Message.kind)\
            .join(Room, Room.room_id == Message.room_id)\
            .join(User, User.user_id == Message.author)\
            .filter(Room.room_id == room_id)\
            .order_by(Message.time_created.desc())\
            .all()
        
        messages_json = []
        for mess in messages:
            messages_json.append({
                "id": int(mess[0]),
                "content": mess[1],
                "author": mess[2],
                "avatar": mess[3],
                "kind": mess[4],
            })

        return messages_json

def update_is_deleted(room_id, is_deleted=False):
    with Session(engine) as session:
        session.query(UserRoom)\
            .filter(UserRoom.room_id == room_id)\
            .update({"is_deleted": is_deleted})
        
        session.commit()

def create_message(room_id, user_id, kind, content):
    with Session(engine) as session:
        session.query(UserRoom)\
            .filter(UserRoom.room_id == room_id)\
            .update({"is_deleted": False})

        message = Message(
            room_id=room_id,
            author=user_id,
            content=content,
            kind=kind
        )
        session.add(message)
        session.commit()
        return message.message_id
    
def delete_chat_by_id(room_id, user_id):
    with Session(engine) as session:
        user_room = session.query(UserRoom).filter(UserRoom.room_id == room_id).filter(UserRoom.user_id == user_id).first()
        if user_room is None:
            return None
        
        user_room.is_deleted = True
        session.add(user_room)
        session.commit()
        return user_room.id

def delete_by_id(room_id):
    with Session(engine) as session:
        room = session.query(Room).filter(Room.room_id == room_id).first()
        if room is None:
            return None
        
        session.delete(room)
        session.commit()
        return room.room_id