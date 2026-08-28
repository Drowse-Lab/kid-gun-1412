package kid_gun_1412.client;

import com.tacz.guns.init.ModItems;
import kid_gun_1412.KidGunMod;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterItemDecorationsEvent;

public final class ClientRegistration {
    private ClientRegistration() {}

    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(KidGunMod.STUCK_CARD.get(), StuckCardRenderer::new);
    }

    public static void registerItemDecorations(RegisterItemDecorationsEvent event) {
        // TaCZ guns all share one item, so the decorator itself filters by GunId.
        event.register(ModItems.MODERN_KINETIC_GUN.get(), new CardGunSlotRenderer());
    }
}
