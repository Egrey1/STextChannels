from ..library import Member, User, deps, TextChannel, con, List

class NewMember(Member):
    async def from_capital(self) -> Member:
        return await deps.capital.fetch_member(self.id)
    
    async def is_a_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.a_transguild.id == role.id for role in mem.roles) if mem else False
    
    async def is_m_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.m_transguild.id == role.id for role in mem.roles) if mem else False
    
class NewUser(User):
    async def from_capital(self) -> Member:
        return await deps.capital.fetch_member(self.id)
    
    async def is_a_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.a_transguild.id == role.id for role in mem.roles) if mem else False
    
    async def is_m_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.m_transguild.id == role.id for role in mem.roles) if mem else False

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

    