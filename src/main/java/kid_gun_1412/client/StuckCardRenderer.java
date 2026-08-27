package kid_gun_1412.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import kid_gun_1412.KidGunMod;
import kid_gun_1412.StuckCardEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import com.mojang.blaze3d.vertex.VertexConsumer;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

public final class StuckCardRenderer extends EntityRenderer<StuckCardEntity> {
    public StuckCardRenderer(EntityRendererProvider.Context context) {
        super(context);
        shadowRadius = 0;
    }
    @Override public void render(StuckCardEntity entity, float yaw, float partialTick, PoseStack pose,
                                 MultiBufferSource buffers, int light) {
        pose.pushPose();
        pose.mulPose(Axis.YP.rotationDegrees(180 - entity.getYRot()));
        // 壁に刺さったカードは長辺を上下にした縦向きで表示する。
        pose.mulPose(Axis.XP.rotationDegrees(entity.getXRot()));
        // Minecraftの1ブロックを約1mとして、実物のカード63×88mmに合わせる。
        pose.scale(0.063f, 0.088f, 1f);
        PoseStack.Pose last = pose.last();
        VertexConsumer vertex = buffers.getBuffer(RenderType.entityCutout(getTextureLocation(entity)));
        quad(vertex, last.pose(), last.normal(), light, -0.5f, -0.5f, 0, 1);
        pose.popPose();
        super.render(entity, yaw, partialTick, pose, buffers, light);
    }
    @Override public ResourceLocation getTextureLocation(StuckCardEntity entity) {
        return new ResourceLocation(KidGunMod.MOD_ID, "textures/entity/cards/" + faceName(entity) + ".png");
    }

    private static String faceName(StuckCardEntity entity) {
        if (entity.isMessage()) return "message";
        int face = Math.floorMod(entity.face(), 54);
        if (face == 52) return "joker_color";
        if (face == 53) return "joker_mono";
        String[] ranks = {"a", "2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k"};
        String[] suits = {"s", "h", "d", "c"};
        return ranks[face % 13] + "_" + suits[face / 13];
    }

    private static void quad(VertexConsumer out, Matrix4f pose, Matrix3f normal, int light,
                             float left, float top, float u0, float u1) {
        out.vertex(pose, left, top + 1, 0).color(255,255,255,255).uv(u0,1).overlayCoords(0).uv2(light).normal(normal,0,0,1).endVertex();
        out.vertex(pose, left + 1, top + 1, 0).color(255,255,255,255).uv(u1,1).overlayCoords(0).uv2(light).normal(normal,0,0,1).endVertex();
        out.vertex(pose, left + 1, top, 0).color(255,255,255,255).uv(u1,0).overlayCoords(0).uv2(light).normal(normal,0,0,1).endVertex();
        out.vertex(pose, left, top, 0).color(255,255,255,255).uv(u0,0).overlayCoords(0).uv2(light).normal(normal,0,0,1).endVertex();
    }
}
