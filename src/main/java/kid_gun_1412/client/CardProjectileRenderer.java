package kid_gun_1412.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.tacz.guns.entity.EntityKineticBullet;
import kid_gun_1412.KidGunMod;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import com.mojang.blaze3d.vertex.VertexConsumer;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Renders the physical card; TaCZ's tracer is disabled in the gun data. */
@Mod.EventBusSubscriber(modid = KidGunMod.MOD_ID, value = Dist.CLIENT)
public final class CardProjectileRenderer {
    private static final ResourceLocation CARD_BACK = new ResourceLocation(
            KidGunMod.MOD_ID, "textures/entity/cards/back_blue.png");
    private CardProjectileRenderer() {}

    @SubscribeEvent
    public static void render(RenderLevelStageEvent event) {
        if (event.getStage() != RenderLevelStageEvent.Stage.AFTER_ENTITIES) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) return;
        Vec3 camera = event.getCamera().getPosition();
        float partial = event.getPartialTick();
        for (net.minecraft.world.entity.Entity raw : mc.level.entitiesForRendering()) {
            if (!(raw instanceof EntityKineticBullet bullet) || !KidGunMod.CARD_GUN.equals(bullet.getGunId())) continue;
            double x = net.minecraft.util.Mth.lerp(partial, bullet.xOld, bullet.getX()) - camera.x;
            double y = net.minecraft.util.Mth.lerp(partial, bullet.yOld, bullet.getY()) - camera.y;
            double z = net.minecraft.util.Mth.lerp(partial, bullet.zOld, bullet.getZ()) - camera.z;
            float open = net.minecraft.util.Mth.clamp((bullet.tickCount + partial) / 2.0f, 0.08f, 1.0f);
            PoseStack pose = event.getPoseStack();
            pose.pushPose();
            pose.translate(x, y, z);
            pose.mulPose(Axis.YP.rotationDegrees(-bullet.getYRot()));
            pose.mulPose(Axis.XP.rotationDegrees(bullet.getXRot()));
            // Keep the long edge vertical, but turn the card plane 90 degrees so
            // its thin edge—not its face—leads along the projectile direction.
            pose.mulPose(Axis.YP.rotationDegrees(90));
            pose.scale(0.063f * open, 0.088f, 0.004f);
            PoseStack.Pose last = pose.last();
            VertexConsumer vertex = mc.renderBuffers().bufferSource().getBuffer(RenderType.entityCutout(CARD_BACK));
            quad(vertex, last.pose(), last.normal(), LightTexture.FULL_BRIGHT);
            pose.popPose();
        }
        mc.renderBuffers().bufferSource().endBatch();
    }

    private static void quad(VertexConsumer out, Matrix4f pose, Matrix3f normal, int light) {
        out.vertex(pose,-0.5f,-0.5f,0).color(255,255,255,255).uv(0,1).overlayCoords(0).uv2(light).normal(normal,0,0,1).endVertex();
        out.vertex(pose, 0.5f,-0.5f,0).color(255,255,255,255).uv(1,1).overlayCoords(0).uv2(light).normal(normal,0,0,1).endVertex();
        out.vertex(pose, 0.5f, 0.5f,0).color(255,255,255,255).uv(1,0).overlayCoords(0).uv2(light).normal(normal,0,0,1).endVertex();
        out.vertex(pose,-0.5f, 0.5f,0).color(255,255,255,255).uv(0,0).overlayCoords(0).uv2(light).normal(normal,0,0,1).endVertex();
    }
}
