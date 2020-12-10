from app import db

class File(db.Model):
    file_hash = db.Column(db.String(32), primary_key=True)
    path = db.Column(db.String)

    def __repr__(self):
        return '<File Hash {}>'.format(self.file_hash)