from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(name="Eak Pun", email="eakpun@gmail.com",
             picture='http://lh3.googleusercontent.com/-W7N4DI18qcc/AAAAAAAAAAI/AAAAAAAAAAA/AKB_U8vFWNOxOUc5EY3-_U0b1Mo8-We_ng/s192-c-mo/photo.jpg')
session.add(user1)
session.commit()

cat1 = Category(name='Baseball',user=user1)
session.add(cat1)
session.commit()

item1 = Item(name="Baseball bat",
             description="A baseball bat is a smooth wooden or metal club used in the sport of baseball to hit the ball after it is thrown by the pitcher.",
             category=cat1, user=user1)
session.add(item1)
session.commit()

cat2 = Category(name='Football',user=user1)
session.add(cat2)
session.commit()

item2 = Item(name="Football",
             description="A large premium footbal.",
             category=cat2, user=user1)
session.add(item2)
session.commit()

print "Added items!"
