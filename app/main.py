from fastapi import FastAPI, status, HTTPException, Response, Depends
from fastapi.params import Body
from typing import List
from random import randrange
from sqlalchemy.orm import Session
import psycopg2
from psycopg2.extras import RealDictCursor
from app import model
from app.database import engine, get_db
from app.schema.post_model import Post

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', 
                            password='Kedro#5791', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("DB connection successful")
except Exception as error:
    print("Connecting to db faild")
    print("Error: ", error)

# Root access
@app.get('/')
def root():
    return {"Hello", "World"}
 
# Get all posts
@app.get('/api/v1/posts', response_model=List[Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(model.Post).all()
    return posts

# Create a Post
@app.post('/api/v1/posts', status_code=status.HTTP_201_CREATED)
def create_post(post:Post, db: Session = Depends(get_db)):
    new_post = model.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"Posts": new_post}

# Get the latest post
@app.get('/api/v1/posts/latest')
def get_latest_post():
    return {"latest": "post"}

# Get A single Post
@app.get('/api/v1/posts/{post_id}', response_model=Post)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(model.Post).filter(model.Post.id == post_id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Can't find post with id: {post_id}")
    return {"Post": post}

# Update Post
@app.put('/api/v1/posts/{post_id}', response_model=Post)
def update_post(post_id: int, post: Post, db: Session = Depends(get_db)):
    post_query = db.query(model.Post).filter(model.Post.id == post_id)
    update_post = post_query.first()
    if not update_post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Can't find post with id: {post_id}")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

# Delete Post
@app.delete('/api/v1/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    delete_post = db.query(model.Post).filter(model.Post.id == post_id)
    if not delete_post.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Can't find post with id: {post_id}")
    delete_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)