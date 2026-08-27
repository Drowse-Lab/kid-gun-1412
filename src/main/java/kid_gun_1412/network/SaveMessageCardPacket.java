package kid_gun_1412.network;

import kid_gun_1412.CardData;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public record SaveMessageCardPacket(InteractionHand hand, String body, String signature) {
    public static void encode(SaveMessageCardPacket packet, FriendlyByteBuf buffer) {
        buffer.writeEnum(packet.hand);
        buffer.writeUtf(packet.body, 256);
        buffer.writeUtf(packet.signature, 32);
    }

    public static SaveMessageCardPacket decode(FriendlyByteBuf buffer) {
        return new SaveMessageCardPacket(buffer.readEnum(InteractionHand.class), buffer.readUtf(256), buffer.readUtf(32));
    }

    public static void handle(SaveMessageCardPacket packet, Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player == null) return;
            ItemStack stack = player.getItemInHand(packet.hand);
            if (!CardData.isMessage(stack) || !CardData.canEdit(stack, player.getUUID())) return;
            String body = packet.body.length() > 256 ? packet.body.substring(0, 256) : packet.body;
            String signature = packet.signature.length() > 32 ? packet.signature.substring(0, 32) : packet.signature;
            if (signature.isBlank()) signature = player.getGameProfile().getName();
            stack.getOrCreateTag().putString(CardData.BODY, body);
            stack.getOrCreateTag().putString(CardData.SIGNATURE, signature);
            stack.getOrCreateTag().putUUID(CardData.AUTHOR, player.getUUID());
            stack.getOrCreateTag().putString(CardData.AUTHOR_NAME, player.getGameProfile().getName());
        });
        context.setPacketHandled(true);
    }
}
