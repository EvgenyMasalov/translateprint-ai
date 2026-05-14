import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database_models import Base, User, Song
import uuid

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
        cls.engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

    def setUp(self):
        Base.metadata.create_all(bind=self.engine)
        self.db = self.TestingSessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def test_user_creation(self):
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        self.db.add(new_user)
        self.db.commit()
        
        db_user = self.db.query(User).filter(User.email == "test@example.com").first()
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user.first_name, "Test")
        self.assertEqual(db_user.id, user_id)

    def test_user_song_relationship(self):
        user_id = str(uuid.uuid4())
        new_user = User(id=user_id, first_name="Test", last_name="User", email="test@example.com")
        self.db.add(new_user)
        self.db.commit()
        
        song_id = str(uuid.uuid4())
        new_song = Song(
            id=song_id,
            user_id=user_id,
            title="Test Song",
            lyrics="Test lyrics"
        )
        self.db.add(new_song)
        self.db.commit()
        
        # Assert
        db_user = self.db.query(User).filter(User.id == user_id).first()
        self.assertEqual(len(db_user.songs), 1)
        self.assertEqual(db_user.songs[0].title, "Test Song")
        
        db_song = self.db.query(Song).filter(Song.id == song_id).first()
        self.assertEqual(db_song.owner.email, "test@example.com")

if __name__ == '__main__':
    unittest.main()
