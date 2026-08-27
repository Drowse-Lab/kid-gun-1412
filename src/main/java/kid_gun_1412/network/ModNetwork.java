package kid_gun_1412.network;

import kid_gun_1412.KidGunMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

public final class ModNetwork {
    private static final String VERSION = "1";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(KidGunMod.MOD_ID, "main"), () -> VERSION, VERSION::equals, VERSION::equals);

    private ModNetwork() {}

    public static void register() {
        CHANNEL.registerMessage(0, SaveMessageCardPacket.class, SaveMessageCardPacket::encode,
                SaveMessageCardPacket::decode, SaveMessageCardPacket::handle);
    }
}
