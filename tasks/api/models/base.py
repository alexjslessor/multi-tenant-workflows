from typing import Any
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session, class_mapper
from sqlalchemy.dialects.postgresql import insert

class Base(DeclarativeBase):

    @classmethod
    def bulk_upsert(
        cls,
        session: Session, 
        data: list[dict[str, Any]], 
        index_column_name: list[str],
        upsert_column_names: list[str]
    ):
        """Bulk upsert helper function using ON CONFLICT DO UPDATE.
        
        ```python
        def bulk_upsert_posts(session: Session, posts: list[dict]):
            # Convert dict keys to match ORM model columns dynamically
            table = class_mapper(RedditPost).mapped_table
            stmt = insert(table).values(posts)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],  # Unique constraint column
                set_={
                    "title": stmt.excluded.title,
                    "score": stmt.excluded.score,
                    "num_comments": stmt.excluded.num_comments,
                    "updated_at": stmt.excluded.updated_at
                }
            )
            session.execute(stmt)
            session.commit()
        ```
        """
        table = class_mapper(cls).mapped_table
        stmt = insert(table).values(data)

        update_fields = {
            col.name: stmt.excluded[col.name] \
                for col in table.columns if col.name in upsert_column_names
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=index_column_name,  
            set_=update_fields
        )
        session.execute(stmt)