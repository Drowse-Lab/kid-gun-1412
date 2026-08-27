package kid_gun_1412;

import com.tacz.guns.api.event.common.GunFireEvent;
import com.tacz.guns.api.event.common.GunReloadEvent;
import com.tacz.guns.api.event.common.EntityHurtByGunEvent;
import com.tacz.guns.api.event.server.AmmoHitBlockEvent;
import com.tacz.guns.entity.EntityKineticBullet;
import com.tacz.guns.api.item.IAmmo;
import com.tacz.guns.api.item.IGun;
import kid_gun_1412.client.MessageCardScreen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.LogicalSide;

public final class CardGunEvents {
    @SubscribeEvent
    public void reload(GunReloadEvent event) {
        if (event.getLogicalSide() != LogicalSide.SERVER || !CardData.isCardGun(event.getGunItemStack())) return;
        CardData.normalize(event.getGunItemStack(), event.getEntity().getRandom());
        IGun gun = IGun.getIGunOrNull(event.getGunItemStack());
        ListTag cylinder = CardData.cylinder(event.getGunItemStack());
        int needed = Math.max(0, 6 - gun.getCurrentAmmoCount(event.getGunItemStack()));
        if (event.getEntity() instanceof Player player) {
            for (int slot = 0; slot < player.getInventory().getContainerSize() && needed > 0; slot++) {
                ItemStack ammo = player.getInventory().getItem(slot);
                IAmmo iAmmo = IAmmo.getIAmmoOrNull(ammo);
                if (iAmmo == null || !KidGunMod.PLAYING_CARD.equals(iAmmo.getAmmoId(ammo))) continue;
                int take = Math.min(needed, ammo.getCount());
                for (int i = 0; i < take; i++) cylinder.add(CardData.fromAmmo(ammo, player.getRandom()));
                needed -= take;
            }
        }
    }

    @SubscribeEvent
    public void fire(GunFireEvent event) {
        if (event.getLogicalSide() != LogicalSide.SERVER || !CardData.isCardGun(event.getGunItemStack())) return;
        CardData.normalize(event.getGunItemStack(), event.getShooter().getRandom());
        ListTag cylinder = CardData.cylinder(event.getGunItemStack());
        if (!cylinder.isEmpty()) {
            CompoundTag fired = cylinder.getCompound(0).copy();
            cylinder.remove(0);
            event.getShooter().getPersistentData().put("Kid1412PendingCard", fired);
        }
    }

    @SubscribeEvent
    public void useCard(PlayerInteractEvent.RightClickItem event) {
        if (!CardData.isMessage(event.getItemStack())) return;
        event.setCancellationResult(InteractionResult.SUCCESS);
        event.setCanceled(true);
        if (event.getLevel().isClientSide) openScreen(event.getHand(), event.getItemStack());
    }

    @SubscribeEvent
    public void bulletCreated(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide || !(event.getEntity() instanceof EntityKineticBullet bullet)
                || !KidGunMod.CARD_GUN.equals(bullet.getGunId()) || bullet.getOwner() == null) return;
        CompoundTag ownerData = bullet.getOwner().getPersistentData();
        if (ownerData.contains("Kid1412PendingCard")) {
            bullet.getPersistentData().put("Kid1412Card", ownerData.getCompound("Kid1412PendingCard").copy());
            ownerData.remove("Kid1412PendingCard");
        }
    }

    @SubscribeEvent
    public void hitBlock(AmmoHitBlockEvent event) {
        if (!KidGunMod.CARD_GUN.equals(event.getAmmo().getGunId())) return;
        net.minecraft.world.phys.BlockHitResult hit = event.getHitResult();
        spawnStuck(event.getAmmo(), hit.getLocation().add(net.minecraft.world.phys.Vec3.atLowerCornerOf(hit.getDirection().getNormal()).scale(0.02)));
    }

    @SubscribeEvent
    public void hitEntity(EntityHurtByGunEvent.Post event) {
        if (event.getLogicalSide() != LogicalSide.SERVER || !KidGunMod.CARD_GUN.equals(event.getGunId())) return;
        spawnStuck(event.getBullet(), event.getHurtEntity().position().add(0, event.getHurtEntity().getBbHeight() * 0.55, 0));
    }

    private static void spawnStuck(net.minecraft.world.entity.Entity bullet, net.minecraft.world.phys.Vec3 location) {
        CompoundTag persistent = bullet.getPersistentData();
        if (persistent.getBoolean("Kid1412CardPlaced")) return;
        CompoundTag card = persistent.contains("Kid1412Card") ? persistent.getCompound("Kid1412Card").copy() : new CompoundTag();
        if (!card.contains(CardData.FACE)) card.putInt(CardData.FACE, bullet.level().getRandom().nextInt(54));
        StuckCardEntity stuck = KidGunMod.STUCK_CARD.get().create(bullet.level());
        if (stuck == null) return;
        stuck.setCard(card);
        stuck.moveTo(location.x, location.y, location.z, bullet.getYRot(), bullet.getXRot());
        bullet.level().addFreshEntity(stuck);
        persistent.putBoolean("Kid1412CardPlaced", true);
    }

    @OnlyIn(Dist.CLIENT)
    private static void openScreen(net.minecraft.world.InteractionHand hand, ItemStack stack) {
        net.minecraft.client.Minecraft.getInstance().setScreen(new MessageCardScreen(hand, stack));
    }
}
