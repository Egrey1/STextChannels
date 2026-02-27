from ..library import con, deps, Row, List, Dict

class Web:
    def __init__(self, name: str | None = None):
        connect = con(deps.DATABASE_MAIN_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute("""
                       SELECT *
                       FROM shares
                       WHERE name = ?
                       """, (name, ))
        fetch = cursor.fetchone()
        connect.close()

        self.name = fetch['name']
        self.description = fetch['description']
        self.channels = fetch['channels']
        self.groups: List[Dict[int, str]]

        for group in fetch['channels']:
            d = {
                'channel_id': int(group.split(',')[0]),
                'webhook_url': group.split(',')[1]
            }
            self.groups.append(d)

    def set_name(self, new_name: str):
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       UPDATE shares
                       SET name = ?
                       WHERE name = ?
                       """, (new_name, self.name))
        connect.commit()
        connect.close()
        self.name = new_name
    
    def set_description(self, new_description: str):
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       UPDATE shares
                       SET description = ?
                       WHERE name = ?
                       """, (new_description, self.name))
        connect.commit()
        connect.close()
        self.description = new_description

    def set_channels(self, channels: str):
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       UPDATE shares
                       SET channels = ?
                       WHERE name = ?
                       """, (channels, self.name))
        connect.commit()
        connect.close()
    
    def add_channel(self, channel_id: int, webhook_url: str):
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        self.channels = self.channels + ';' + str(channel_id) + ',' + webhook_url if self.channels else str(channel_id) + ',' + webhook_url

        cursor.execute("""
                       UPDATE shares
                       SET channels = ?
                       WHERE name = ?
                       """, (self.channels, self.name)
                       )
        connect.commit()
        connect.close()

        self.groups.append(
            {
                'channel_id': channel_id,
                'webhook_url': webhook_url
            }
        )
        