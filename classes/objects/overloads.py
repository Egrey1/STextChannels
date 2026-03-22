from ..library import Member, User, deps, TextChannel, con, List, datetime, logging, Guild, run, Embed

class NewMember(Member):
    async def from_capital(self) -> Member:
        return await deps.capital.fetch_member(self.id)
    
    async def is_a_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.a_transguild.id == role.id for role in mem.roles) if mem else False
    
    async def is_m_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.m_transguild.id == role.id for role in mem.roles) if mem else False
    
    async def is_OPSK(self) -> bool: 
        mem = await self.from_capital()
        return any(deps.OPSK_role.id == role.id for role in mem.roles) if mem else False
    
    async def is_citadel_leader(self) -> bool:
        mem = await self.from_capital()
        return any(deps.leader_role.id == role.id for role in mem.roles) if mem else False

    def muted(self, value: datetime = None) -> bool | datetime:
        """Return False if not muted or expired, else expiration datetime."""
        if value is None:
            try:
                with deps.main_db as connect:
                    cursor = connect.cursor()
                    cursor.execute(
                        """
                        SELECT muted_up
                        FROM users
                        WHERE user_id = ?
                        """,
                        (self.id,),
                    )
                    fetch = cursor.fetchone()
                    cursor.close()

                if not fetch or not fetch[0]:
                    return False
                until = datetime.fromisoformat(fetch[0])
                if datetime.now() >= until:
                    self.unmute_web()
                    return False
                return until
            except Exception as e:
                logging.error(f'Ошибка в muted: {e}')
                return False
        # set new time
        try:
            iso = value.isoformat() if isinstance(value, datetime) else str(value)
            with deps.main_db as connect:
                cursor = connect.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (user_id, muted_up)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO
                    UPDATE SET muted_up = excluded.muted_up
                    """,
                    (self.id, iso),
                )
                connect.commit()
                cursor.close()
        except Exception as e:
            logging.error(f'Ошибка в muted: {e}')
    
    def where_muted(self, value: str = None) -> List[str]:
        if not value:
            try:
                with deps.main_db as connect:
                    connect = con(deps.DATABASE_MAIN_PATH)
                    cursor = connect.cursor()

                    cursor.execute("""
                                SELECT where_muted
                                FROM users
                                WHERE user_id = ?
                                """, (self.id,))
                    fetch = cursor.fetchone()
                    cursor.close()

                    return fetch[0].split(';') if fetch[0] else None
            except Exception as e:
                logging.error(f'Ошибка в where_muted: {e}')
                return None
        
        # Временно убрали
        # before = ''.join(self.where_muted())
        # if before is not None:
        #     value = before + ';' + value

        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            INSERT INTO users (user_id, where_muted)
                            VALUES (?, ?)
                            ON CONFLICT(user_id) DO
                            UPDATE SET
                            where_muted = excluded.where_muted
                            """, (self.id, value))
                connect.commit()
                cursor.close()
        except Exception as e:
            logging.info(f'Ошибка в where_muted: {e}')
    
    def mute_web(self, time: datetime | str, where: str):
        if self.where_muted is None:
            raise ValueError('Он в мьюте везде')
        if isinstance(time, datetime):
            self.muted = time
        else:
            self.muted = datetime.fromisoformat(time)
        self.where_muted = where
    
    def unmute_web(self):
        try:
            with deps.main_db as connect:
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
                cursor.close()
        except Exception as e:
            logging.info(f'Ошибка в unmute_web: {e}')

    def get_money(self):
        try:
            with deps.economic_db as connect:
                cursor = connect.cursor()
                a = self.id

                cursor.execute("""
                               SELECT money
                               FROM user_balances
                               WHERE user_id = ?
                               """, (self.id, ))
                fetch = cursor.fetchone()
                cursor.close()

                return int(fetch['money']) if fetch is not None else 0
        except Exception as e:
            logging.error(f'Ошибка в get_money: {e}')

    async def set_money(self, value: int, member: Member | None = None):
        try:
            with deps.economic_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               INSERT INTO user_balances (user_id, money)
                               VALUES (?, ?)
                               ON CONFLICT(user_id) DO
                               UPDATE SET money = excluded.money
                               """, (self.id, value))
                connect.commit()
                cursor.close()

                embed = Embed(title='Константное изменение баланса', description=f'У кого: {self.name}\nНовое значение: {value}')
                if member:
                    embed.set_footer(text=f'Вызвал: {member.name}', icon_url=member.avatar.url)

                await deps.economicLogs.send(embed=embed)
        except Exception as e:
            logging.error(f'Ошибка в set_money: {e}')
    
    async def add_money(self, value: int, member: Member | None = None):
        try:
            new_value = int(self.get_money()) + value
            with deps.economic_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               INSERT INTO user_balances (user_id, money)
                               VALUES (?, ?)
                               ON CONFLICT(user_id) DO
                               UPDATE SET money = excluded.money
                               """, (self.id, new_value))
                connect.commit()
                cursor.close()

                embed = Embed(title='Изменение баланса', description=f'У кого: {self.name}\nНа сколько: {value}\nНовый баланс: {new_value}')
                if member:
                    embed.set_footer(text=f'Вызвал: {member.name}', icon_url=member.avatar.url)

                await deps.economicLogs.send(embed=embed)
        except Exception as e:
            logging.error(f'Ошибка в add_money: {e}')

    async def is_a_shop(self):
        mem = await self.from_capital()
        return any(deps.a_shop.id == role.id for role in mem.roles) if mem else False
    
class NewUser(User):
    async def from_capital(self) -> Member:
        return await deps.capital.fetch_member(self.id)
    
    async def is_a_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.a_transguild.id == role.id for role in mem.roles) if mem else False
    
    async def is_m_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.m_transguild.id == role.id for role in mem.roles) if mem else False
    
    async def is_OPSK(self) -> bool: 
        mem = await self.from_capital()
        return any(deps.OPSK_role.id == role.id for role in mem.roles) if mem else False

    async def is_citadel_leader(self) -> bool:
        mem = await self.from_capital()
        return any(deps.leader_role.id == role.id for role in mem.roles) if mem else False

    def muted(self, value: datetime = None) -> bool | None:
        if not value:
            try:
                with deps.main_db as connect:
                    cursor = connect.cursor()

                    cursor.execute("""
                                SELECT muted_up
                                FROM users
                                WHERE user_id = ?
                                """, (self.id,))
                    fetch = cursor.fetchone()
                    cursor.close()

                    return bool(fetch[0]) if fetch else None
            except Exception as e:
                logging.error(f'Ошибка в muted: {e}')
                return None
            
        
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            INSERT INTO users (user_id, muted_up)
                            VALUES (?, ?)
                            ON CONFLICT(user_id) DO
                            UPDATE SET
                            muted_up = excluded.muted_up
                            """, (value.isoformat(), self.id))
                connect.commit()
                cursor.close()
        except Exception as e:
            logging.error(f'Ошибка в muted: {e}')
    
    def where_muted(self, value: str = None) -> List[str]:
        if not value:
            try:
                with deps.main_db as connect:
                    connect = con(deps.DATABASE_MAIN_PATH)
                    cursor = connect.cursor()

                    cursor.execute("""
                                SELECT where_muted
                                FROM users
                                WHERE user_id = ?
                                """, (self.id,))
                    fetch = cursor.fetchone()
                    cursor.close()

                    return fetch[0].split(';') if fetch[0] else None
            except Exception as e:
                logging.error(f'Ошибка в where_muted: {e}')
                return None
        
        # Временно убрали
        # before = ''.join(self.where_muted())
        # if before is not None:
        #     value = before + ';' + value

        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            INSERT INTO users (user_id, where_muted)
                            VALUES (?, ?)
                            ON CONFLICT(user_id) DO
                            UPDATE SET
                            where_muted = excluded.where_muted
                            """, (self.id, value))
                connect.commit()
                cursor.close()
        except Exception as e:
            logging.info(f'Ошибка в where_muted: {e}')
    
    def mute_web(self, time: datetime | str, where: str):
        if self.where_muted is None:
            raise ValueError('Он в мьюте везде')
        if isinstance(time, datetime):
            self.muted = time
        else:
            self.muted = datetime.fromisoformat(time)
        self.where_muted = where
    
    def unmute_web(self):
        try:
            with deps.main_db as connect:
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
                cursor.close()
        except Exception as e:
            logging.info(f'Ошибка в unmute_web: {e}')

    def get_money(self):
        try:
            with deps.economic_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               SELECT money
                               FROM user_balances
                               WHERE user_id = ?
                               """, (self.id, ))
                fetch = cursor.fetchone()
                cursor.close()

                return fetch['money'] if fetch is not None else 0
        except Exception as e:
            logging.error(f'Ошибка в get_money: {e}')

    async def set_money(self, value: int, member: Member | None = None):
        try:
            with deps.economic_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               INSERT INTO user_balances (user_id, money)
                               VALUES (?, ?)
                               ON CONFLICT(user_id) DO
                               UPDATE SET money = excluded.money
                               """, (self.id, value))
                connect.commit()
                cursor.close()

                embed = Embed(
                    title='Константное изменение баланса', 
                    description=f'У кого: {self.name}\nНовое значение: {value}'
                    )
                
                if member:
                    embed.set_footer(text=f'Вызвал: {member.name}', icon_url=member.avatar.url)

                await deps.economicLogs.send(embed=embed)
        except Exception as e:
            logging.error(f'Ошибка в set_money: {e}')
    
    async def add_money(self, value: int, member: Member | None = None):
        try:
            new_value = int(self.get_money()) + value
            with deps.economic_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               INSERT INTO user_balances (user_id, money)
                               VALUES (?, ?)
                               ON CONFLICT(user_id) DO
                               UPDATE SET money = excluded.money
                               """, (self.id, new_value))
                connect.commit()
                cursor.close()

                embed = Embed(
                    title='Изменение баланса', 
                    description=f'У кого: {self.name}\nНа сколько: {value}\nНовый баланс: {new_value}'
                    )
                
                if member:
                    embed.set_footer(text=f'Вызвал: {member.name}', icon_url=member.avatar.url)

                await deps.economicLogs.send(embed=embed)
        except Exception as e:
            logging.error(f'Ошибка в add_money: {e}')

    async def is_a_shop(self):
        mem = await self.from_capital()
        return any(deps.a_shop.id == role.id for role in mem.roles) if mem else False
        

class New_TextChannel(TextChannel):
    def get_all_webs(self) -> List[deps.Web]:
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute(f"""
                            SELECT name
                            FROM shares
                            WHERE channels LIKE '%{self.id},%'
                            """)
                fetch = cursor.fetchall()
                cursor.close()

                return [deps.Web(name[0]) for name in fetch]
        except Exception as e:
            logging.error(f'Ошибка в get_all_webs: {e}')
            return []


class NewGuild(Guild):
    def get_money(self):
        try:
            with deps.economic_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               SELECT money
                               FROM guild_balances
                               WHERE guild_id = ?
                               """, (self.id, ))
                
                fetch = cursor.fetchone()
                cursor.close()

                return int(fetch['money']) if fetch is not None else 0
        except Exception as e:
            logging.error(f'Ошибка в get_money: {e}')

    async def set_money(self, value: int, member: Member | None = None):
        try:
            with deps.economic_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               INSERT INTO guild_balances (guild_id, money)
                               VALUES (?, ?)
                               ON CONFLICT(guild_id) DO
                               UPDATE SET money = excluded.money
                               """, (self.id, value))
                connect.commit()
                cursor.close()

                embed = Embed(
                    title='Константное изменение баланса сервера', 
                    description=f'У какого: {self.name}\nНовое значение: {value}'
                    )
                
                if member:
                    embed.set_footer(text=f'Вызвал: {member.name}', icon_url=member.avatar.url)

                await deps.economicLogs.send(embed=embed)
        except Exception as e:
            logging.error(f'Ошибка в set_money: {e}')
    
    async def add_money(self, value: int, member: Member | None = None):
        try:
            new_value = int(self.get_money()) + value
            with deps.economic_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               INSERT INTO guild_balances (guild_id, money)
                               VALUES (?, ?)
                               ON CONFLICT(guild_id) DO
                               UPDATE SET money = excluded.money
                               """, (self.id, new_value))
                connect.commit()
                cursor.close()

                embed = Embed(
                    title='Изменение баланса сервера', 
                    description=f'У какого: {self.name}\nНа сколько: {value}\nНовый баланс: {new_value}'
                    )
                
                if member:
                    embed.set_footer(text=f'Вызвал: {member.name}', icon_url=member.avatar.url)

                await deps.economicLogs.send(embed=embed)
        except Exception as e:
            logging.error(f'Ошибка в add_money: {e}')

    async def guild_partner(self) -> deps.GuildPartner | None:
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               SELECT *
                               FROM `guild-partner`
                               WHERE id = ?
                               """, (self.id, ))
                fetch = cursor.fetchone()
                cursor.close()

                if not fetch:
                    return None
                marks = []

                for mark in fetch['marks'].split(';'):
                    if mark == 'т':
                        mark = 'телемост'
                    elif mark == 'м':
                        mark = 'магазин'
                    marks.append(mark)

                channel = await deps.capital.fetch_channel(int(fetch['channel_id']))
                
                return deps.GuildPartner(fetch['name'], fetch['piar_text'], fetch['description'], channel, tuple(marks), self.id)
        except Exception as e:
            logging.error(f'Ошибка в guild_partner: {e}')