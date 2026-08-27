package kid_gun_1412;

import com.tacz.guns.api.item.IGun;
import com.tacz.guns.api.item.builder.AmmoItemBuilder;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.item.ItemStack;

import java.util.UUID;

public final class CardData {
    public static final String MESSAGE = "Kid1412Message";
    public static final String BODY = "Kid1412Body";
    public static final String SIGNATURE = "Kid1412Signature";
    public static final String AUTHOR = "Kid1412Author";
    public static final String AUTHOR_NAME = "Kid1412AuthorName";
    public static final String FACE = "Kid1412Face";
    public static final String CYLINDER = "Kid1412Cylinder";

    private CardData() {}

    public static ItemStack createMessageCard() {
        ItemStack stack = AmmoItemBuilder.create().setId(KidGunMod.PLAYING_CARD).setCount(1).build();
        stack.getOrCreateTag().putBoolean(MESSAGE, true);
        stack.setHoverName(net.minecraft.network.chat.Component.translatable("item.kid_gun_1412.message_card"));
        return stack;
    }

    public static boolean isMessage(ItemStack stack) {
        return stack.hasTag() && stack.getTag().getBoolean(MESSAGE);
    }

    public static boolean isCardGun(ItemStack stack) {
        IGun gun = IGun.getIGunOrNull(stack);
        return gun != null && KidGunMod.CARD_GUN.equals(gun.getGunId(stack));
    }

    public static CompoundTag fromAmmo(ItemStack ammo, net.minecraft.util.RandomSource random) {
        CompoundTag card = new CompoundTag();
        card.putBoolean(MESSAGE, isMessage(ammo));
        card.putInt(FACE, isMessage(ammo) ? 54 : random.nextInt(54));
        if (ammo.hasTag()) {
            copy(ammo.getTag(), card, BODY);
            copy(ammo.getTag(), card, SIGNATURE);
            copy(ammo.getTag(), card, AUTHOR);
            copy(ammo.getTag(), card, AUTHOR_NAME);
        }
        return card;
    }

    private static void copy(CompoundTag from, CompoundTag to, String key) {
        if (from.contains(key)) to.put(key, from.get(key).copy());
    }

    public static ListTag cylinder(ItemStack gunStack) {
        CompoundTag tag = gunStack.getOrCreateTag();
        if (!tag.contains(CYLINDER, Tag.TAG_LIST)) tag.put(CYLINDER, new ListTag());
        return tag.getList(CYLINDER, Tag.TAG_COMPOUND);
    }

    public static void normalize(ItemStack gunStack, net.minecraft.util.RandomSource random) {
        IGun gun = IGun.getIGunOrNull(gunStack);
        if (gun == null) return;
        ListTag list = cylinder(gunStack);
        int amount = Math.min(6, gun.getCurrentAmmoCount(gunStack));
        while (list.size() > amount) list.remove(list.size() - 1);
        while (list.size() < amount) list.add(fromAmmo(ItemStack.EMPTY, random));
    }

    public static boolean canEdit(ItemStack stack, UUID player) {
        CompoundTag tag = stack.getOrCreateTag();
        return !tag.hasUUID(AUTHOR) || tag.getUUID(AUTHOR).equals(player);
    }
}
