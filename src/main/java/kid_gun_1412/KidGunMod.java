package kid_gun_1412;

import com.mojang.logging.LogUtils;
import com.tacz.guns.api.item.builder.AmmoItemBuilder;
import com.tacz.guns.api.item.builder.GunItemBuilder;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import org.slf4j.Logger;

@Mod(KidGunMod.MOD_ID)
public final class KidGunMod {
    public static final String MOD_ID = "kid_gun_1412";
    public static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation CARD_GUN = new ResourceLocation("kid1412", "card_gun");
    private static final ResourceLocation PLAYING_CARD = new ResourceLocation("kid1412", "playing_card");
    private static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MOD_ID);

    static {
        TABS.register("main", () -> CreativeModeTab.builder()
                .title(Component.translatable("itemGroup.kid_gun_1412"))
                .icon(() -> GunItemBuilder.create().setId(CARD_GUN).setAmmoCount(12).build())
                .displayItems((parameters, output) -> {
                    output.accept(GunItemBuilder.create().setId(CARD_GUN).setAmmoCount(12).build());
                    output.accept(AmmoItemBuilder.create().setId(PLAYING_CARD).setCount(32).build());
                }).build());
    }

    public KidGunMod() {
        GunPackInstaller.install();
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        TABS.register(modBus);
    }
}
