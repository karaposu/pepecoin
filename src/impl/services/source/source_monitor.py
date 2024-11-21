import psutil
from pydantic import AnyUrl, BaseModel, EmailStr, Field

# def get_disk_space():
#     return "Disk space usage: 75%"
#
# def get_memory_usage():
#     return "Memory usage: 60%"
#
# def get_gpu_usage():
#     return "GPU usage: 40%"
#
# def get_queue_lengths():
#     return "Queue lengths: 5"
from impl.services.base_service import BaseService
class SourceMonitoringService(BaseService):
    def check_compatibility(self):
        pass

    def preprocess_request_data(self):
        pass
    def process_request(self):
        monitor_results = self.prepare_response_for_source_monitoring()
        self.response =monitor_results
        return monitor_results
    def get_disk_space(self):
        self.disk_space= "Disk space usage: 75%"
        return   self.disk_space

    def get_memory_usage(self):
        self.memory_usage = "Memory usage: 60%"
        return self.memory_usage

    def get_gpu_usage(self):
        self.gpu_usage = "GPU usage: 40%"
        return self.gpu_usage

    def get_queue_lengths(self):
        self.queue_length = "Queue lengths: 5"
        return self.queue_length

    def pack_all_info(self):
        pass
        # image_result=ImagesDataforUserImageManipulationResponse(head=head,
        #                                   headselection_mask=headselection_mask,
        #                                   head_transparent=head_transparent)
        #
        #
        # response_data = UserImageManipulationResponseData(images=image_result,
        #                                                       fd_coordinates=fd_coordinates,
        #                                                       skin_color=skin_color,
        #                                                       lm_coordinates=lm_coordinates )
        # return response_data

    def prepare_response_for_source_monitoring(self):
        def bytes_to_gb(bytes, round_digits=2):
            return round(bytes / (1024 ** 3), round_digits)

        disk = psutil.disk_usage('/')
        memory = psutil.virtual_memory()

        # Convert each attribute to GB
        disk_total_gb = bytes_to_gb(disk.total)
        disk_used_gb = bytes_to_gb(disk.used)
        disk_free_gb = bytes_to_gb(disk.free)

        memory_total_gb = bytes_to_gb(memory.total)
        memory_available_gb = bytes_to_gb(memory.available)

        # Placeholder values
        gpu_usage = "50%"
        queue_lengths = "42"

        return SystemMonitoringResponse(
            disk_space_usage=f"Total: {disk_total_gb} GB, Used: {disk_used_gb} GB, Free: {disk_free_gb} GB",
            memory_usage=f"Total: {memory_total_gb} GB, Available: {memory_available_gb} GB",
            gpu_usage=gpu_usage,
            queue_lengths=queue_lengths
        )


    # DATA_IS_VALID, unpacked_data = unpack_dom_image_package(mandomimage_post_request)




class SystemMonitoringResponse(BaseModel):
    disk_space_usage: str
    memory_usage: str
    gpu_usage: str  # This requires a more specialized approach, possibly with a library like GPUtil
    queue_lengths: str  # This is highly application-specific


def prepare_response_for_source_monitoring():
    def bytes_to_gb(bytes, round_digits=2):
        return round(bytes / (1024 ** 3), round_digits)

    disk = psutil.disk_usage('/')
    memory = psutil.virtual_memory()

    # Convert each attribute to GB
    disk_total_gb = bytes_to_gb(disk.total)
    disk_used_gb = bytes_to_gb(disk.used)
    disk_free_gb = bytes_to_gb(disk.free)

    memory_total_gb = bytes_to_gb(memory.total)
    memory_available_gb = bytes_to_gb(memory.available)

    # Placeholder values
    gpu_usage = "50%"
    queue_lengths = "42"

    return SystemMonitoringResponse(
        disk_space_usage=f"Total: {disk_total_gb} GB, Used: {disk_used_gb} GB, Free: {disk_free_gb} GB",
        memory_usage=f"Total: {memory_total_gb} GB, Available: {memory_available_gb} GB",
        gpu_usage=gpu_usage,
        queue_lengths=queue_lengths
    )



    return SystemMonitoringResponse(
        disk_space_usage=f"Total: {disk_usage.total}, Used: {disk_usage.used}, Free: {disk_usage.free}",
        memory_usage=f"Total: {memory_usage.total}, Available: {memory_usage.available}",
        gpu_usage=gpu_usage,
        queue_lengths=queue_lengths
    )

