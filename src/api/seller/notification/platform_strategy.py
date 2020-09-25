from scarface.platform_strategy import (
    APNPlatformStrategy, APNSSandboxPlatformStrategy, PlatformStrategy)


# Note: Until a PR on scarface is merged, this is a hacky way
# to get mutable-content working


class APSMixin(object):
    def format_payload(self, message):
        payload = self.format_push(
            message.badge_count,
            message.context,
            message.context_id,
            message.has_new_content,
            message.message, message.sound
        )

        if message.extra_payload:
            if 'aps' in message.extra_payload:
                # Handle `aps` updating separately to not loose
                # any alert props
                payload['aps'].update(message.extra_payload.pop('aps'))
                # payload['aps']['mutable-content'] = 1
            if 'large_image' in message.extra_payload:
                payload['aps']['mutable-content'] = 1
            payload.update(message.extra_payload)
            # payload['aps']['mutable-content'] = 1

        return PlatformStrategy.format_payload(self, payload)


class ApplePlatformStrategy(APSMixin, APNPlatformStrategy):
    """Override platform strategy
    """
    pass


class AppleSandboxPlatformStrategy(APSMixin, APNSSandboxPlatformStrategy):
    pass
