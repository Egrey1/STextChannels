from ..library import Member, User, deps

class NewMember(Member):
    async def from_capital(self) -> Member:
        return await deps.capital.fetch_member(self.id)
    
    async def is_a_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.a_transguild.id == role.id for role in mem.roles) if mem else False
    
class NewUser(User):
    async def from_capital(self) -> Member:
        return await deps.capital.fetch_member(self.id)
    
    async def is_a_transguild(self) -> bool:
        mem = await self.from_capital()
        return any(deps.a_transguild.id == role.id for role in mem.roles) if mem else False