from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(name="Eak Mock", email="eakmock@gmail.com",
             picture='http://lh3.googleusercontent.com/-W7N4DI18qcc/AAAAAAAAAAI/AAAAAAAAAAA/AKB_U8vFWNOxOUc5EY3-_U0b1Mo8-We_ng/s192-c-mo/photo.jpg')
session.add(user1)
session.commit()

cat1 = Category(name='Baseball',user=user1)
session.add(cat1)
session.commit()

item1 = Item(name="Baseball bat",
             description="A baseball",
             price="100",
             picture="https://www.baseballsavings.com/wcsstore/CatalogAssetStore/Attachment/images/products/baseball/P101443/1-z.jpg",
             category=cat1, user=user1)
session.add(item1)
session.commit()

cat2 = Category(name='Football',user=user1)
session.add(cat2)
session.commit()

item2 = Item(name="Football",
             description="A large premium footbal.",
             price="59",
             picture="https://n2.sdlcdn.com/imgs/b/e/o/Nike-Football-SDL771347869-1-56a7c.jpg",
             category=cat2, user=user1)
session.add(item2)
session.commit()

print "Added items!"
