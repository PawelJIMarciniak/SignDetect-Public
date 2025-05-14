from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, UniqueConstraint, DateTime, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Language(Base):
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class Sign(Base):
    __tablename__ = 'signs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    languages_id = Column(Integer, ForeignKey('languages.id'), nullable=False)
    name = Column(String, nullable=False)
    is_dynamic = Column(Integer, nullable=False)
    body_parts_count = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('is_dynamic IN (0, 1)', name='check_is_dynamic'),
    )

    language = relationship("Language", back_populates="signs")


Language.signs = relationship("Sign", order_by=Sign.id, back_populates="language")


class BodyPart(Base):
    __tablename__ = 'body_parts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)


class BodyPartsPerSign(Base):
    __tablename__ = 'body_parts_per_signs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    signs_id = Column(Integer, ForeignKey('signs.id'), nullable=False)
    body_parts_id = Column(Integer, ForeignKey('body_parts.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('signs_id', 'body_parts_id', name='unique_sign_body_part'),
    )

    sign = relationship("Sign", back_populates="body_parts")
    body_part = relationship("BodyPart", back_populates="signs")


Sign.body_parts = relationship("BodyPartsPerSign", order_by=BodyPartsPerSign.id, back_populates="sign")
BodyPart.signs = relationship("BodyPartsPerSign", order_by=BodyPartsPerSign.id, back_populates="body_part")


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_name = Column(String, nullable=False, unique=True)
    learning_consent = Column(Integer, nullable=False)
    device_manufacturer = Column(String)
    device_model = Column(String)

    __table_args__ = (
        CheckConstraint('learning_consent IN (0, 1)', name='check_learning_consent'),
    )


class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    signs_id = Column(Integer, ForeignKey('signs.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    frame_count = Column(Integer, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    image_width = Column(Integer)
    image_height = Column(Integer)

    sign = relationship("Sign", back_populates="videos")
    author = relationship("Author", back_populates="videos")


Sign.videos = relationship("Video", order_by=Video.id, back_populates="sign")
Author.videos = relationship("Video", order_by=Video.id, back_populates="author")


class BodyPartsPerVideo(Base):
    __tablename__ = 'body_parts_per_videos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    videos_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    body_parts_id = Column(Integer, ForeignKey('body_parts.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('videos_id', 'body_parts_id', name='unique_video_body_part'),
    )

    video = relationship("Video", back_populates="body_parts")
    body_part = relationship("BodyPart", back_populates="videos")


Video.body_parts = relationship("BodyPartsPerVideo", order_by=BodyPartsPerVideo.id, back_populates="video")
BodyPart.videos = relationship("BodyPartsPerVideo", order_by=BodyPartsPerVideo.id, back_populates="body_part")


class Frame(Base):
    __tablename__ = 'frames'
    id = Column(Integer, primary_key=True, autoincrement=True)
    videos_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    frame_number = Column(Integer, nullable=False)

    video = relationship("Video", back_populates="frames")


Video.frames = relationship("Frame", order_by=Frame.id, back_populates="video")


class PointNumber(Base):
    __tablename__ = 'point_numbers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    point_number = Column(Integer, nullable=False)
    point_name = Column(String)


class FrameCoordinate(Base):
    __tablename__ = 'frame_coordinates'
    frame_id = Column(Integer, ForeignKey('frames.id'), primary_key=True)
    point_number_id = Column(Integer, ForeignKey('point_numbers.id'), primary_key=True)
    x_coordinate = Column(DECIMAL(20, 2))
    y_coordinate = Column(DECIMAL(20, 2))
    z_coordinate = Column(DECIMAL(20, 2))

    frame = relationship("Frame", back_populates="coordinates")
    point_number = relationship("PointNumber", back_populates="coordinates")


Frame.coordinates = relationship("FrameCoordinate", order_by=FrameCoordinate.frame_id, back_populates="frame")
PointNumber.coordinates = relationship("FrameCoordinate", order_by=FrameCoordinate.point_number_id, back_populates="point_number")
