package kid_gun_1412.client;

import com.tacz.guns.api.item.IGun;
import kid_gun_1412.KidGunMod;
import kid_gun_1412.CardData;
import net.minecraft.nbt.ListTag;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = KidGunMod.MOD_ID, value = Dist.CLIENT)
public final class CardCylinderHud {
    private static final ResourceLocation CARD_GUN = new ResourceLocation("kid1412", "card_gun");
    private static final int[][] OFFSETS = {{0, -11}, {10, -6}, {10, 6}, {0, 11}, {-10, 6}, {-10, -6}};

    private CardCylinderHud() {}

    @SubscribeEvent
    public static void render(RenderGuiOverlayEvent.Post event) {
        // Attach once to Forge's hotbar pass. RenderGuiOverlayEvent is fired for every
        // overlay; without this guard the cylinder was an independent repeated HUD.
        if (!event.getOverlay().id().equals(VanillaGuiOverlay.HOTBAR.id())) {
            return;
        }
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.player == null || minecraft.options.hideGui) {
            return;
        }
        ItemStack stack = minecraft.player.getMainHandItem();
        IGun gun = IGun.getIGunOrNull(stack);
        if (gun == null || !CARD_GUN.equals(gun.getGunId(stack))) {
            return;
        }

        int ammo = Math.max(0, Math.min(6, gun.getCurrentAmmoCount(stack)));
        ListTag cylinder = CardData.cylinder(stack);
        GuiGraphics graphics = event.getGuiGraphics();
        // TaCZ GunHudOverlay draws the gun icon at width-117..width-78 and the
        // numeric ammo counter to its right. Extend that native panel on the left.
        int centerX = graphics.guiWidth() - 135;
        int centerY = graphics.guiHeight() - 37;
        graphics.fill(graphics.guiWidth() - 120, graphics.guiHeight() - 51,
                graphics.guiWidth() - 119, graphics.guiHeight() - 23, 0xCCFFFFFF);
        graphics.fill(centerX - 3, centerY - 3, centerX + 4, centerY + 4, 0xCC10141A);

        for (int slot = 0; slot < 6; slot++) {
            int x = centerX + OFFSETS[slot][0];
            int y = centerY + OFFSETS[slot][1];
            boolean loaded = slot < ammo;
            int border = slot == 0 ? 0xFFFFFFFF : 0xFF68727E;
            boolean message = loaded && slot < cylinder.size() && cylinder.getCompound(slot).getBoolean(CardData.MESSAGE);
            int fill = !loaded ? 0x99151A20 : message ? 0xFFF4F0DF : 0xFF2A65B7;
            graphics.fill(x - 3, y - 5, x + 4, y + 6, border);
            graphics.fill(x - 2, y - 4, x + 3, y + 5, fill);
            if (loaded) {
                int mark = message ? 0xFFB4162B : 0xFFB9D5F4;
                graphics.fill(x - 1, y - 2, x + 2, y - 1, mark);
                graphics.fill(x - 1, y + 1, x + 2, y + 2, mark);
            }
        }
    }
}
