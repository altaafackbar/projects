from bsddb3 import db

database = db.DB()
database.set_flags(db.DB_DUP) 
database.open('da.idx',None, db.DB_BTREE, db.DB_CREATE)
database.close()

database = db.DB()
database.set_flags(db.DB_DUP) 
database.open('em.idx',None, db.DB_BTREE, db.DB_CREATE)
database.close()

database = db.DB()
database.set_flags(db.DB_DUP) 
database.open('te.idx',None, db.DB_BTREE, db.DB_CREATE)
database.close()

database = db.DB()
database.set_flags(db.DB_DUP) 
database.open('re.idx',None, db.DB_HASH, db.DB_CREATE)
database.close()
