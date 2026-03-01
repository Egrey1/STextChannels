from ..library import Member, User, deps, TextChannel, con, List, datetime

class NewMember(Member):
    async def from_capital(self) -> Member:
        return await deps.capital.fetch_member(self.id)
    
    async def is_a_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.a_transguild.id == role.id for role in mem.roles) if mem else False
    
    async def is_m_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.m_transguild.id == role.id for role in mem.roles) if mem else False
    
    def muted(self, value: datetime = None) -> bool | None:
        if not value:
            connect = con(deps.DATABASE_MAIN_PATH)
            cursor = connect.cursor()

            cursor.execute("""
                        SELECT muted_up
                        FROM users
                        WHERE user_id = ?
                        """, (self.id,))
            fetch = cursor.fetchone()

            return bool(fetch[0]) if fetch else None
        
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       INSERT INTO users (user_id, muted_up)
                       VALUES (?, ?)
                       ON CONFLICT(user_id) DO
                       UPDATE SET
                       muted_up = excluded.muted_up
                       """, (value.isoformat(), self.id))
        connect.commit()
        connect.close()
    def where_muted(self, value: str = None) -> List[str]:
        if not value:
            connect = con(deps.DATABASE_MAIN_PATH)
            cursor = connect.cursor()

            cursor.execute("""
                        SELECT where_muted
                        FROM users
                        WHERE user_id = ?
                        """, (self.id,))
            fetch = cursor.fetchone()

            return fetch[0].split(';') if fetch[0] else None
        
        # Временно убрали
        # before = ''.join(self.where_muted())
        # if before is not None:
        #     value = before + ';' + value
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        

        cursor.execute("""
                       INSERT INTO users (user_id, where_muted)
                       VALUES (?, ?)
                       ON CONFLICT(user_id) DO
                       UPDATE SET
                       where_muted = excluded.where_muted
                       """, (self.id, value))
        connect.commit()
        connect.close()
    
    def mute_web(self, time: datetime | str, where: str):
        if self.where_muted is None:
            raise ValueError('Он в мьюте везде')
        if isinstance(time, datetime):
            self.muted = time
        else:
            self.muted = datetime.fromisoformat(time)
        self.where_muted = where
    
    def unmute_web(self):
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       UPDATE users
                       SET muted_up = NULL
                       WHERE user_id = ?
                       """, (self.id,))
        cursor.execute("""
                       UPDATE users
                       SET where_muted = NULL
                       WHERE user_id = ?
                       """, (self.id,))
        connect.commit()
        connect.close()

class NewUser(User):
    async def from_capital(self) -> Member:
        return await deps.capital.fetch_member(self.id)
    
    async def is_a_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.a_transguild.id == role.id for role in mem.roles) if mem else False
    
    async def is_m_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.m_transguild.id == role.id for role in mem.roles) if mem else False
    
    def muted(self, value: datetime):
        if not value:
            connect = con(deps.DATABASE_MAIN_PATH)
            cursor = connect.cursor()

            cursor.execute("""
                        SELECT muted_up
                        FROM users
                        WHERE user_id = ?
                        """, (self.id,))
            fetch = cursor.fetchone()

            return bool(fetch[0])
        
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       INSERT INTO users (user_id, muted_up)
                       VALUES (?, ?)
                       ON CONFLICT(user_id) DO
                       UPDATE SET
                       muted_up = excluded.muted_up
                       """, (value.isoformat(), self.id))
        connect.commit()
        connect.close()
    def where_muted(self, value: str):
        if not value:
            connect = con(deps.DATABASE_MAIN_PATH)
            cursor = connect.cursor()

            cursor.execute("""
                        SELECT where_muted
                        FROM users
                        WHERE user_id = ?
                        """, (self.id,))
            fetch = cursor.fetchone()

            return fetch[0].split(';') if fetch[0] else None
        
        # Временно убрали
        # before = ''.join(self.where_muted())
        # if before is not None:
        #     value = before + ';' + value
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        

        cursor.execute("""
                       INSERT INTO users (user_id, where_muted)
                       VALUES (?, ?)
                       ON CONFLICT(user_id) DO
                       UPDATE SET
                       where_muted = excluded.where_muted
                       """, (self.id, value))
        connect.commit()
        connect.close()
    
    def mute_web(self, time: datetime | str, where: str):
        if self.where_muted is None:
            raise ValueError('Он в мьюте везде')
        if isinstance(time, datetime):
            self.muted = time
        else:
            self.muted = datetime.fromisoformat(time)
        self.where_muted = where
    
    def unmute_web(self):
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       UPDATE users
                       SET muted_up = NULL
                       WHERE user_id = ?
                       """, (self.id,))
        cursor.execute("""
                       UPDATE users
                       SET where_muted = NULL
                       WHERE user_id = ?
                       """, (self.id,))
        connect.commit()
        connect.close()

class New_TextChannel(TextChannel):
    def get_all_webs(self) -> List[deps.Web]:
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                       SELECT name
                       FROM shares
                       WHERE channels LIKE '%{self.id},%'
                       """)
        fetch = cursor.fetchall()

        return [deps.Web(name[0]) for name in fetch]

    