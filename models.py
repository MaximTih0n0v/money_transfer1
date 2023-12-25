from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    TIMESTAMP,
    ForeignKey,
    Boolean,
    func
)
from sqlalchemy.orm import (
    relationship,
    declarative_base,
)
from db_conn import DBConnector
from db_engine import url_engine

Base = declarative_base()


class User(Base):
    __tablename__: str = 'user'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)
    surname = Column(String(30))
    phone = Column(String(50), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP)

    bank_numbers = relationship("BankAccount", back_populates="user")


class BankAccount(Base):
    __tablename__ = 'bank_account'

    bank_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    balance = Column(Float, server_default='0')
    card_number = Column(String(30), unique=True, nullable=False)
    PIN = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP)

    user = relationship('User', back_populates="bank_numbers")


db_connector = DBConnector(db_url=url_engine)
db_connector.create_tables(Base)
