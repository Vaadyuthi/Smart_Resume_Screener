from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .database import Base


class Resume(Base):

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    filename: Mapped[str] = mapped_column(
        String(255)
    )

    name: Mapped[str] = mapped_column(
        String(255),
        default="Unknown"
    )

    email: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    phone: Mapped[str] = mapped_column(
        String(100),
        default=""
    )

    skills: Mapped[str] = mapped_column(
        Text,
        default="[]"
    )

    education: Mapped[str] = mapped_column(
        Text,
        default="[]"
    )

    experience: Mapped[str] = mapped_column(
        Text,
        default="[]"
    )

    raw_text: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class ScreeningResult(Base):

    __tablename__ = "screening_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    resume_id: Mapped[int] = mapped_column(
        Integer,
        index=True
    )

    job_description: Mapped[str] = mapped_column(
        Text
    )

    score: Mapped[float] = mapped_column(
        Float
    )

    strengths: Mapped[str] = mapped_column(
        Text,
        default="[]"
    )

    gaps: Mapped[str] = mapped_column(
        Text,
        default="[]"
    )

    recommendation: Mapped[str] = mapped_column(
        String(100)
    )

    justification: Mapped[str] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )