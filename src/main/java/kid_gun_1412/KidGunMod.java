package kid_gun_1412;

import com.mojang.logging.LogUtils;
import com.tacz.guns.api.item.builder.AmmoItemBuilder;
import com.tacz.guns.api.item.builder.GunItemBuilder;
import kid_gun_1412.network.ModNetwork;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;

@Mod(KidGunMod.MOD_ID)
public final class KidGunMod {
    public static final String MOD_ID = "kid_gun_1412";
    public static final Logger LOGGER = LogUtils.getLogger();
    public static final ResourceLocation CARD_GUN = new ResourceLocation("kid1412", "card_gun");
    public static final ResourceLocation PLAYING_CARD = new ResourceLocation("kid1412", "playing_card");
    private static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MOD_ID);
    private static final DeferredRegister<EntityType<?>> ENTITIES =
            DeferredRegister.create(Registries.ENTITY_TYPE, MOD_ID);
    public static final RegistryObject<EntityType<StuckCardEntity>> STUCK_CARD = ENTITIES.register("stuck_card",
            () -> EntityType.Builder.<StuckCardEntity>of(StuckCardEntity::new, MobCategory.MISC)
                    .sized(0.07f, 0.01f).clientTrackingRange(64).updateInterval(10)
                    .build(MOD_ID + ":stuck_card"));

    static {
        TABS.register("main", () -> CreativeModeTab.builder()
                .title(Component.translatable("itemGroup.kid_gun_1412"))
                .icon(() -> GunItemBuilder.create().setId(CARD_GUN).setAmmoCount(6).build())
                .displayItems((parameters, output) -> {
                    output.accept(GunItemBuilder.create().setId(CARD_GUN).setAmmoCount(6).build());
                    // Forge requires every stack shown in a creative tab to have a count of 1.
                    output.accept(AmmoItemBuilder.create().setId(PLAYING_CARD).setCount(1).build());
                    output.accept(CardData.createMessageCard());
                }).build());
    }

    public KidGunMod() {
        GunPackInstaller.install();
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        TABS.register(modBus);
        ENTITIES.register(modBus);
        modBus.addListener(kid_gun_1412.client.ClientRegistration::registerRenderers);
        ModNetwork.register();
        MinecraftForge.EVENT_BUS.register(new CardGunEvents());
    }
}
