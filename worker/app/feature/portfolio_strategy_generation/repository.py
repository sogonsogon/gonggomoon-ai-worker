from sqlalchemy import select, BigInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class PostAnalysisModel(Base):
    __tablename__ = "post_analysis"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class PostAnalysisNotFoundError(Exception):
    pass


class SqlAlchemyPostAnalysisRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def get_title_and_summary(self, post_analysis_id: int) -> tuple[str, str]:
        with self.session_factory() as session:
            stmt = select(PostAnalysisModel.title, PostAnalysisModel.summary).where(
                PostAnalysisModel.id == post_analysis_id
            )
            row = session.execute(stmt).one_or_none()

        if row is None:
            raise PostAnalysisNotFoundError(f"post analysis not found: {post_analysis_id}")

        title, summary = row
        return title or "", summary or ""
