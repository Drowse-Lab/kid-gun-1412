package kid_gun_1412;

import kid_gun_1412.client.MessageViewScreen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

public final class StuckCardEntity extends Entity {
    private static final EntityDataAccessor<Boolean> MESSAGE = SynchedEntityData.defineId(StuckCardEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> FACE = SynchedEntityData.defineId(StuckCardEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<String> BODY = SynchedEntityData.defineId(StuckCardEntity.class, EntityDataSerializers.STRING);
    private static final EntityDataAccessor<String> SIGNATURE = SynchedEntityData.defineId(StuckCardEntity.class, EntityDataSerializers.STRING);
    private CompoundTag card = new CompoundTag();

    public StuckCardEntity(EntityType<? extends StuckCardEntity> type, Level level) { super(type, level); }

    @Override protected void defineSynchedData() {
        entityData.define(MESSAGE, false);
        entityData.define(FACE, 0);
        entityData.define(BODY, "");
        entityData.define(SIGNATURE, "");
    }

    public void setCard(CompoundTag value) {
        card = value.copy();
        entityData.set(MESSAGE, value.getBoolean(CardData.MESSAGE));
        entityData.set(FACE, value.getInt(CardData.FACE));
        entityData.set(BODY, value.getString(CardData.BODY));
        entityData.set(SIGNATURE, value.getString(CardData.SIGNATURE));
    }

    public boolean isMessage() { return entityData.get(MESSAGE); }
    public int face() { return entityData.get(FACE); }
    public String body() { return entityData.get(BODY); }
    public String signature() { return entityData.get(SIGNATURE); }

    @Override public void tick() {
        super.tick();
        setDeltaMovement(0, 0, 0);
        if (!level().isClientSide && !isMessage() && tickCount >= 200) discard();
    }

    @Override public InteractionResult interact(Player player, InteractionHand hand) {
        if (!isMessage()) return InteractionResult.PASS;
        if (level().isClientSide) openView();
        return InteractionResult.sidedSuccess(level().isClientSide);
    }

    @net.minecraftforge.api.distmarker.OnlyIn(net.minecraftforge.api.distmarker.Dist.CLIENT)
    private void openView() {
        net.minecraft.client.Minecraft.getInstance().setScreen(new MessageViewScreen(body(), signature()));
    }

    @Override public boolean hurt(DamageSource source, float amount) {
        if (level().isClientSide) return true;
        if (isMessage()) {
            ItemStack drop = CardData.createMessageCard();
            CompoundTag tag = drop.getOrCreateTag();
            tag.merge(card.copy());
            spawnAtLocation(drop);
        }
        discard();
        return true;
    }

    @Override public boolean isPickable() { return true; }
    @Override protected void readAdditionalSaveData(CompoundTag tag) { setCard(tag.getCompound("Card")); }
    @Override protected void addAdditionalSaveData(CompoundTag tag) { tag.put("Card", card.copy()); }
}
