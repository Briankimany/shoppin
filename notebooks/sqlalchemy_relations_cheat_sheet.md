
### 📘 SQLAlchemy Relationships Cheat Sheet

#### 🔁 One-to-Many Relationship (e.g. Author → Book)

```python
class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship("Author", back_populates="books")
```

- `back_populates`: Explicitly defines both sides of a relationship.
- `backref`: Automatically creates the reverse relationship.

---

#### 🔄 Many-to-Many Relationship with Association Table

```python
book_tag = Table(
    'book_tag',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    tags = relationship('Tag', secondary=book_tag, backref='books')

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

- `secondary`: Specifies the association table for many-to-many relationships.
- `backref`: Creates the reverse side automatically in `Tag`.

---

#### 🔁 Relationship Cascade Options

| Option           | Behavior                                                                 |
|------------------|--------------------------------------------------------------------------|
| `all`            | Includes all operations (save, update, delete, merge, etc.)              |
| `save-update`    | Propagates save/update to related objects                                |
| `merge`          | Merges related objects from one session into another                     |
| `delete`         | Deletes related objects when the parent is deleted                       |
| `delete-orphan`  | Deletes child objects when removed from parent’s relationship collection |

**Example:**
```python
books = relationship("Book", cascade="all, delete-orphan")
```

---

#### ⏳ Relationship Loading Strategies

| Strategy     | Behavior                                                                 |
|--------------|--------------------------------------------------------------------------|
| `select`     | (Default) Lazy load – loads related objects on access                    |
| `joined`     | Eager load – loads in the same query using JOIN                          |
| `subquery`   | Eager load – uses a separate subquery                                    |
| `noload`     | Disables automatic loading                                               |
| `dynamic`    | Returns a query object instead of a list (for large collections)         |

**Example:**
```python
tags = relationship('Tag', secondary=book_tag, backref='books', lazy='joined')
```

---

#### ❓ What Happens If You Don't Use `backref` or `back_populates`?

- The relationship will be **unidirectional**.
- You can access related objects only from the side that defines the `relationship()`.
- Reverse access requires a manual query.

---

Let me know if you want me to export this to a file or expand with additional examples!Absolutely! Here's a summarized version of everything we've covered, formatted as a Markdown (`.md`) file:

---

### 📘 SQLAlchemy Relationships Cheat Sheet

#### 🔁 One-to-Many Relationship (e.g. Author → Book)

```python
class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship("Author", back_populates="books")
```

- `back_populates`: Explicitly defines both sides of a relationship.
- `backref`: Automatically creates the reverse relationship.

---

#### 🔄 Many-to-Many Relationship with Association Table

```python
book_tag = Table(
    'book_tag',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    tags = relationship('Tag', secondary=book_tag, backref='books')

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

- `secondary`: Specifies the association table for many-to-many relationships.
- `backref`: Creates the reverse side automatically in `Tag`.

---

#### 🔁 Relationship Cascade Options

| Option           | Behavior                                                                 |
|------------------|--------------------------------------------------------------------------|
| `all`            | Includes all operations (save, update, delete, merge, etc.)              |
| `save-update`    | Propagates save/update to related objects                                |
| `merge`          | Merges related objects from one session into another                     |
| `delete`         | Deletes related objects when the parent is deleted                       |
| `delete-orphan`  | Deletes child objects when removed from parent’s relationship collection |

**Example:**
```python
books = relationship("Book", cascade="all, delete-orphan")
```

---

#### ⏳ Relationship Loading Strategies

| Strategy     | Behavior                                                                 |
|--------------|--------------------------------------------------------------------------|
| `select`     | (Default) Lazy load – loads related objects on access                    |
| `joined`     | Eager load – loads in the same query using JOIN                          |
| `subquery`   | Eager load – uses a separate subquery                                    |
| `noload`     | Disables automatic loading                                               |
| `dynamic`    | Returns a query object instead of a list (for large collections)         |

**Example:**
```python
tags = relationship('Tag', secondary=book_tag, backref='books', lazy='joined')
```

---

#### ❓ What Happens If You Don't Use `backref` or `back_populates`?

- The relationship will be **unidirectional**.
- You can access related objects only from the side that defines the `relationship()`.
- Reverse access requires a manual query.

