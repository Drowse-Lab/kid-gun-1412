package kid_gun_1412.client;

import com.mojang.blaze3d.platform.Lighting;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.tacz.guns.api.item.IGun;
import kid_gun_1412.KidGunMod;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.IItemDecorator;

/**
 * Draws the card gun's actual bedrock model in inventory slots.
 *
 * <p>TaCZ hardcodes {@link ItemDisplayContext#GUI} to the display json's flat {@code slot}
 * texture, so a gun pack alone can never show a live model in the inventory. Because this add-on
 * ships as its own mod we can go around that: the gun pack's slot texture is left blank and a
 * Forge item decorator re-renders the same stack in {@link ItemDisplayContext#FIXED}, which is one
 * of the contexts TaCZ does route through its 3D path.
 */
public final class CardGunSlotRenderer implements IItemDecorator {
    /** Roughly matches how the gun sits in TaCZ's own slot art. */
    private static final float PITCH = 18.0F;
    private static final float YAW = -32.0F;
    private static final float ROLL = -6.0F;
    /** The model is about a block long; shrink it to leave a margin inside the 16px slot. */
    private static final float FIT = 0.86F;

    @Override
    public boolean render(GuiGraphics graphics, Font font, ItemStack stack, int x, int y) {
        IGun gun = IGun.getIGunOrNull(stack);
        if (gun == null) {
            return false;
        }
        ResourceLocation gunId = gun.getGunId(stack);
        if (!KidGunMod.CARD_GUN.equals(gunId)) {
            return false;
        }

        PoseStack pose = graphics.pose();
        pose.pushPose();
        // Same setup vanilla uses for a slot item, then a three quarter turn on top of it.
        pose.translate(x + 8.0F, y + 8.0F, 150.0F);
        pose.scale(16.0F * FIT, -16.0F * FIT, 16.0F * FIT);
        pose.mulPose(Axis.XP.rotationDegrees(PITCH));
        pose.mulPose(Axis.YP.rotationDegrees(YAW));
        pose.mulPose(Axis.ZP.rotationDegrees(ROLL));

        Lighting.setupFor3DItems();
        Minecraft.getInstance().getItemRenderer().renderStatic(
                stack, ItemDisplayContext.FIXED, LightTexture.FULL_BRIGHT,
                OverlayTexture.NO_OVERLAY, pose, graphics.bufferSource(), null, 0);
        graphics.flush();
        pose.popPose();
        // The slot texture is blank, so nothing of TaCZ's flat art is left to hide.
        return true;
    }
}
