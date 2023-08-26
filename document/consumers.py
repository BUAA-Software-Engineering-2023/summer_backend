from asgiref.sync import sync_to_async
from channels_yroom.consumer import YroomConsumer

from user.models import User


def get_tiptap_room_name(room_name: str) -> str:
    # The room prefix is 'textcollab_tiptap.'
    return "textcollab_tiptap.%s" % room_name


class TipTapConsumer(YroomConsumer):
    def get_room_name(self) -> str:
        user_id = self.scope['url_route']['kwargs']['user']
        return get_tiptap_room_name(user_id)

    async def connect(self) -> None:
        try:
            user_id = self.scope['url_route']['kwargs']['user']
            try:
                user = await sync_to_async(User.objects.get)(pk=user_id)
            except User.DoesNotExist:
                await self.close()
                return

            await super().connect()
        except:
            print('============================')