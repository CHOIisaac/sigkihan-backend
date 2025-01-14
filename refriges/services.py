# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# from .models import RefrigeratorInvitation
#
#
# def create_invitation(inviter, invitee_email, refrigerator):
#     # 초대 생성
#     invitation = RefrigeratorInvitation.objects.create(
#         inviter=inviter,
#         invitee_email=invitee_email,
#         refrigerator=refrigerator,
#     )
#     send_invitation_via_websocket(invitation)
#     return invitation
#
#
# def send_invitation_via_websocket(invitation):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         f'invitations_{invitation.refrigerator.id}',
#         {
#             'type': 'send_invitation',
#             'message': {
#                 'id': invitation.id,
#                 'inviter': invitation.inviter.name,
#                 'refrigerator': invitation.refrigerator.name,
#                 'status': invitation.status,
#                 'created_at': str(invitation.created_at),
#             }
#         }
#     )