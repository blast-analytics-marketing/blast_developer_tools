"""
Extract, Transform, Load (ETL) Processor class
"""
import os
import sys
import inspect
import subprocess
import pprint as pp
from pathlib import Path
from blast_defaults import SUCCESS, FAILURE

MODULE_PATH = Path(__file__).resolve()
CWD_PATH = Path(__file__).resolve().parent


class EtlProcessor:
    """ EtlProcessor class """

    def __init__(
            self,
            staging_table: str,
            extractor_path: Path,
            cmd_args: list,
            loader,
            transformer,
            run_extract=True,
            run_load=True,
            run_transform=True,
            logger=None,
            debug=False,
    ):
        """ initialize class """
        self.__cls_name = f"{type(self).__name__}"
        self.__staging_table = staging_table
        self.__extractor_path = extractor_path
        self.__cmd_args = ["python", str(self.__extractor_path)]
        # cmd_args must be list of strings only
        self.__cmd_args.extend([str(val) for val in cmd_args])
        self.__loader = loader
        self.__transformer = transformer
        self.__logger = logger
        self.__debug = debug
        # what needs to happen
        self.__run_extract = run_extract
        self.__run_load = run_load
        self.__run_transform = run_transform
        # state of EtlProcessor
        self.__is_extracted = False
        self.__is_loaded = False
        self.__is_transformed = False

    def __str__(self) -> str:
        """returns informal name of class, called by str()"""
        return f"{self.__cls_name} {self.__staging_table}"

    def __repr__(self) -> str:
        """returns official string representation of class, called by repr()"""
        return (f"{self.__cls_name} {self.__staging_table} "
                f"is_extracted: {self.__is_extracted} "
                f"is_loaded: {self.__is_loaded} {self.__loader} "
                f"is_transformed: {self.__is_transformed} {self.__loader}")

    def show_state(self) -> None:
        """displays all class variables (types and values)"""
        print(f"\n{MODULE_PATH}")
        for key, val in self.__dict__.items():
            print(f"self.{key:36} {str(type(val)):36}\t '{val}'")

    def show_data(self, title: str, data) -> None:
        """displays all data values"""
        print(f"\n{self.__cls_name} {title}")
        pp.pprint(data, indent=2, width=160, compact=True, sort_dicts=False)

    def __log_info(self, msg: str) -> None:
        """print message to console if logger=None"""
        self.__logger.info(msg) if self.__logger else print(msg)

    def __log_failures(self) -> None:
        """log reason if successful() returns false vs. warning no data"""
        if self.__run_extract != self.__is_extracted:
            self.__log_info(msg=f"{FAILURE} is_extracted | '{self.__staging_table}'")
        if self.__run_load != self.__is_loaded:
            self.__log_info(msg=f"{FAILURE} is_loaded | {self.__loader}")
        if self.__run_transform != self.__is_transformed:
            self.__log_info(msg=f"{FAILURE} is_transformed | {self.__transformer}")

    def __log_exception(self, error_msg: str = None) -> None:
        """ custom exception handling logging function."""
        ex_type, ex_value, ex_tb = sys.exc_info()
        ex_type = f"{ex_type}" if ex_type else ""
        ex_value = " ".join(f"{str(ex_value)}".split()) if ex_value else ""
        src_name = f"{os.path.split(ex_tb.tb_frame.f_code.co_filename)[1]}"
        base_msg = f"{ex_type} {ex_value} | {src_name}:{ex_tb.tb_lineno}"
        exc_msg = f"{error_msg} | {base_msg}" if error_msg else base_msg
        self.__logger.error(exc_msg) if self.__logger else print(exc_msg)

    def run(self) -> None:
        """ run the data retrieval and ETL processing """
        method = f"{inspect.currentframe().f_code.co_name}()"
        try:
            # extract from data source
            if self.__run_extract:
                self.extract()
            # proceed with loading
            if self.__run_load and self.extracted():
                self.__loader.load()
                self.__is_loaded = self.__loader.loaded()
            # checks extractor and loader state
            if self.__run_transform and self.extracted() and self.loaded():
                self.__transformer.transform()
                self.__is_transformed = self.__transformer.transformed()
        except Exception:
            self.__log_exception(error_msg=f"{method} {FAILURE} '{self.__staging_table}'")

    def extract(self) -> None:
        """ runs the extraction of data and logs the results """
        method = f"{inspect.currentframe().f_code.co_name}()"
        timeout = 240
        print(f"{method} processing: '{self.__staging_table}'")
        try:
            # each arg separated by comma ',' and convert pathlib object to string
            print(f"{' '.join(self.__cmd_args)}")
            # universal_newlines=True to return text not byte stream, shell=False if args=list
            with subprocess.Popen(
                    args=self.__cmd_args,
                    shell=False,
                    universal_newlines=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
            ) as proc:
                # blocking wait, subprocess already logs info/errors
                proc_stdout, proc_stderr = proc.communicate(input=None, timeout=timeout)
                print(f"{proc_stdout}")
                if proc_stderr:
                    stderr = str(proc_stderr).replace('\n', '')
                    self.__log_info(
                        msg=f"{method} returncode: {proc.returncode} = '{os.strerror(proc.returncode)}'"
                            f"stderr: {stderr}"
                        )
                # only update flag if extractor returns successfully
                if proc.returncode == 0:
                    self.__is_extracted = True
        except FileNotFoundError:
            self.__log_exception(error_msg=f"{method} {FAILURE} subprocess.Popen command line")
        except subprocess.TimeoutExpired:
            self.__log_info(msg=f"{method} {FAILURE} subprocess ({timeout}s) timeout expired")
            proc.kill()

    def extracted(self) -> bool:
        """ returns status of extractor"""
        return self.__is_extracted

    def loaded(self) -> bool:
        """ returns status of loader"""
        return self.__loader.loaded()

    def transformed(self) -> bool:
        """ returns status of transformer"""
        return self.__transformer.transformed()

    def successful(self) -> bool:
        """ returns ETL success or failure """
        # self.__log_failures()
        if not self.__run_load:
            return self.extracted()
        if not self.__run_transform:
            return self.extracted() and self.loaded()
        return self.extracted() and self.loaded() and self.transformed()
