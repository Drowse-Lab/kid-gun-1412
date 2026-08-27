package kid_gun_1412.client;

import kid_gun_1412.KidGunMod;
import net.minecraftforge.client.event.EntityRenderersEvent;

public final class ClientRegistration {
    private ClientRegistration() {}
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(KidGunMod.STUCK_CARD.get(), StuckCardRenderer::new);
    }
}
