from sqlalchemy.orm import Session
from models.models import *
from services.db import engine

def create(article_id, user_id, content):
    with Session(engine) as session:
        comment = Comment(
            author=user_id,
            article_id=article_id,
            content=content,
        )
        session.add(comment)
        session.commit()
        return comment.comment_id

def get_all(article_id, user_id, role):
    with Session(engine) as session:
        comments = session.query(Comment.comment_id, Comment.article_id, Comment.content, Comment.time_created, Comment.time_updated, User.user_id, User.fullname, User.avatar)\
            .join(User, User.user_id == Comment.author)\
            .filter(Comment.article_id == article_id).all()
        comments_json = []
        
        for comment in comments:
            is_modify = False

            if role != "student" or comment[5] == user_id:
                is_modify = True

            comments_json.append({
                "id": comment[0],
                "article_id": comment[1],
                "content": comment[2],
                "time_created": comment[3],
                "time_updated": comment[4],
                "isModify": is_modify,
                "author": {
                    "id": comment[5],
                    "fullname": comment[6],
                    "avatar": comment[7],
                },
            })

        return comments_json
    
def get_by_id(comment_id):
    with Session(engine) as session:
        comment = session.query(Comment.comment_id, Comment.article_id, User.user_id, User.avatar, Comment.content, Comment.time_created, Comment.time_updated)\
            .join(User, User.user_id == Comment.author)\
            .filter(Comment.comment_id == comment_id)\
            .first()
        
        if comment is None:
            return None
        
        return {
            "id": comment[0],
            "article_id": comment[1],
            "author": {
                "id": comment[2],
                "avatar": comment[3]
            },
            "content": comment[4],
            "time_created": comment[5],
            "time_updated": comment[6]
        }

def update_by_id(comment_id, content):
    with Session(engine) as session:
        comment = session.query(Comment).filter(Comment.comment_id == comment_id).first()
        if comment is None:
            return None
        
        comment.content = content
        session.add(comment)
        session.commit()
        return comment_id
    
def delete_by_id(comment_id):
    with Session(engine) as session:
        comment = session.query(Comment).filter(Comment.comment_id == comment_id).first()
        if comment is None:
            return None
        
        session.delete(comment)
        session.commit()
        return comment_id